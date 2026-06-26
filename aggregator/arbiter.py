import os
import json
import logging
import argparse

from config import Config


###############################################################################
# The 4 metrics compared across sources, in display order.
###############################################################################
METRICS = ['price_usd', 'market_cap', 'network_hashrate', 'difficulty']


def initialize_logger(level: str) -> None:
    log_level = logging.INFO

    if level == 'debug':
        log_level = logging.DEBUG
    elif level == 'warn':
        log_level = logging.WARNING
    elif level == 'error':
        log_level = logging.ERROR
    elif level == 'info':
        log_level = logging.INFO

    formatter = logging.Formatter(
        fmt='[%(levelname)s][%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=log_level, handlers=[console_handler])


def to_float(value):
    """Convert a raw value to a strictly positive float, or None.

    Handles strings (optionally prefixed with '$' or containing commas),
    sentinel values (-1), None / empty strings, and values <= 0.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '').strip()
        if not value:
            return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if result <= 0.0:
        return None
    return result


def load_json(folder_output: str, *parts):
    """Load a JSON file from the dataset folder; return None if missing or unreadable."""
    path = os.path.join(folder_output, *parts)
    if not os.path.exists(path):
        logging.warning(f'⚠️ File not found, source skipped: {path}')
        return None
    try:
        with open(path) as fd:
            return json.load(fd)
    except (json.JSONDecodeError, OSError) as err:
        logging.warning(f'⚠️ Cannot read [{path}]: {err}')
        return None


###############################################################################
# Loaders: one function per source -> dict[TICKER_UPPER] -> record
# record = { name, algorithm?, price_usd?, market_cap?,
#            network_hashrate?, difficulty? } (only fields > 0)
###############################################################################
def load_coinpaprika(folder_output: str) -> dict:
    data = load_json(folder_output, 'coinpaprika', 'tickers.json')
    if not isinstance(data, list):
        return {}

    coins = {}
    ranks = {}
    for entry in data:
        ticker = (entry.get('symbol') or '').upper()
        if not ticker:
            continue

        # Internal dedup: keep the best rank (lowest rank > 0).
        rank = entry.get('rank') or 0
        rank = rank if rank > 0 else float('inf')
        if ticker in ranks and ranks[ticker] <= rank:
            continue

        usd = (entry.get('quotes') or {}).get('USD') or {}
        record = {'name': entry.get('name')}
        record['price_usd'] = to_float(usd.get('price'))
        record['market_cap'] = to_float(usd.get('market_cap'))

        coins[ticker] = record
        ranks[ticker] = rank

    return coins


def load_hashrate_no(folder_output: str) -> dict:
    data = load_json(folder_output, 'hashrate_no', 'coins.json')
    if not isinstance(data, dict):
        return {}

    coins = {}
    for entry in data.values():
        ticker = (entry.get('ticker') or '').upper()
        if not ticker:
            continue

        price = (entry.get('price') or {}).get('USD')
        network = entry.get('network') or {}
        coins[ticker] = {
            'name': entry.get('name'),
            'algorithm': entry.get('algorithm'),
            'price_usd': to_float(price),
            'network_hashrate': to_float(network.get('hashrate')),
            'difficulty': to_float(network.get('difficulty')),
        }

    return coins


def load_whattomine(folder_output: str) -> dict:
    data = load_json(folder_output, 'whattomine', 'coins.json')
    if not isinstance(data, dict):
        return {}

    coins = {}
    for name, entry in (data.get('coins') or {}).items():
        ticker = (entry.get('tag') or '').upper()
        if not ticker:
            continue

        # whattomine does not expose a USD price (exchange_rate is in BTC).
        coins[ticker] = {
            'name': name,
            'algorithm': entry.get('algorithm'),
            'market_cap': to_float(entry.get('market_cap')),
            'network_hashrate': to_float(entry.get('nethash')),
            'difficulty': to_float(entry.get('difficulty')),
        }

    return coins


def load_binance(folder_output: str) -> dict:
    folder = os.path.join(folder_output, 'binance', 'price')
    if not os.path.isdir(folder):
        logging.warning(f'⚠️ Folder not found, source skipped: {folder}')
        return {}

    coins = {}
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith('.json'):
            continue

        data = load_json(folder, filename)
        if not isinstance(data, dict):
            continue

        symbol = (data.get('symbol') or '').upper()
        if not symbol.endswith('USD'):
            continue

        ticker = symbol[:-3]  # BTCUSD -> BTC
        if not ticker:
            continue

        # Binance only provides a pair price, not a coin name: we deliberately
        # omit 'name' to avoid false identity collisions (e.g. ETH != "Ethereum").
        coins[ticker] = {
            'price_usd': to_float(data.get('price')),
        }

    return coins


###############################################################################
# Aggregation: { TICKER -> { source_name -> record } }
###############################################################################
def aggregate_sources(folder_output: str) -> dict:
    # Only external API sources are compared. The '*_manager' folders
    # (data already merged by the aggregator) and 'arbiter' (this script's
    # output) are intentionally excluded.
    sources = {
        'coinpaprika': load_coinpaprika(folder_output),
        'hashrate_no': load_hashrate_no(folder_output),
        'whattomine': load_whattomine(folder_output),
        'binance': load_binance(folder_output),
    }

    by_ticker = {}
    for source_name, coins in sources.items():
        for ticker, record in coins.items():
            by_ticker.setdefault(ticker, {})[source_name] = record

    logging.info(
        f'🔄 {len(by_ticker)} tickers aggregated from '
        f'{len([s for s in sources.values() if s])} sources'
    )
    return by_ticker, sources


###############################################################################
# Detections
###############################################################################
def normalize_name(name: str) -> str:
    """'Ethereum Classic' / 'ethereumclassic' -> 'ethereumclassic'."""
    if not name:
        return ''
    return ''.join(c for c in name.lower() if c.isalnum())


def detect_identity_collisions(by_ticker: dict) -> list:
    """Same ticker but diverging coin names across sources."""
    collisions = []

    for ticker in sorted(by_ticker):
        per_source = by_ticker[ticker]

        named = {
            src: rec['name']
            for src, rec in per_source.items()
            if rec.get('name')
        }
        if len(named) < 2:
            continue

        normalized = {normalize_name(n) for n in named.values()}
        if len(normalized) > 1:
            collisions.append({'ticker': ticker, 'names': named})

    return collisions


def detect_value_divergences(by_ticker: dict, threshold: float) -> list:
    """Each metric is compared independently across sources.

    For each ticker and each metric, collect all values > 0 per source;
    if >= 2 values exist and (max - min) / min > threshold, flag a divergence.
    """
    divergences = []

    for ticker in sorted(by_ticker):
        per_source = by_ticker[ticker]

        for metric in METRICS:
            values = {
                src: rec[metric]
                for src, rec in per_source.items()
                if rec.get(metric) is not None
            }
            if len(values) < 2:
                continue

            min_src = min(values, key=values.get)
            max_src = max(values, key=values.get)
            min_value = values[min_src]
            max_value = values[max_src]

            spread = (max_value - min_value) / min_value
            if spread > threshold:
                divergences.append({
                    'ticker': ticker,
                    'metric': metric,
                    'min_source': min_src,
                    'min_value': min_value,
                    'max_source': max_src,
                    'max_value': max_value,
                    'spread': spread,
                    'values': values,
                })

    divergences.sort(key=lambda d: d['spread'], reverse=True)
    return divergences


###############################################################################
# Markdown rendering
###############################################################################
def format_value(value: float) -> str:
    """Human-readable display: scientific notation for extreme values."""
    if value >= 1e9 or (0 < value < 1e-4):
        return f'{value:.6g}'
    return f'{value:,.6g}'


def render_report(by_ticker: dict, sources: dict, collisions: list,
                  divergences: list, threshold: float) -> str:
    active_sources = [name for name, coins in sources.items() if coins]

    lines = []
    lines.append('# Arbiter Report — identity collisions & value divergences across APIs')
    lines.append('')
    lines.append(f'- Sources analysed: {len(active_sources)} '
                 f'({", ".join(active_sources)})')
    lines.append(f'- Tickers compared: {len(by_ticker)}')
    lines.append(f'- Divergence threshold: {threshold:.0%}')
    lines.append(f'- Identity collisions: {len(collisions)}')
    lines.append(f'- Value divergences: {len(divergences)}')
    lines.append('')

    ###########################################################################
    # Table 1 — Identity collisions
    ###########################################################################
    lines.append('## Identity Collisions')
    lines.append('')
    lines.append('Same ticker, but different coin names across sources.')
    lines.append('To mark a row as resolved, replace `☐` with `☑` or `✓`.')
    lines.append('')

    if not collisions:
        lines.append('_No collisions detected._')
    else:
        header_sources = [name for name in sources if sources[name]]
        lines.append('| Ticker | ' + ' | '.join(header_sources) + ' | Done |')
        lines.append('|' + '---|' * (len(header_sources) + 1) + '---|')
        for col in collisions:
            cells = [col['ticker']]
            for src in header_sources:
                cells.append(col['names'].get(src, '—'))
            cells.append('☐')
            lines.append('| ' + ' | '.join(cells) + ' |')
    lines.append('')

    ###########################################################################
    # Table 2 — Value divergences (each metric independently)
    ###########################################################################
    lines.append('## Value Divergences')
    lines.append('')
    lines.append(f'Relative spread `(max - min) / min` above {threshold:.0%}. '
                 'Each metric is compared independently.')
    lines.append('To mark a row as resolved, replace `☐` with `☑` or `✓`.')
    lines.append('')

    if not divergences:
        lines.append('_No divergences detected._')
    else:
        lines.append('| Ticker | Metric | Min (source) | Max (source) '
                     '| Spread % | All sources | Done |')
        lines.append('|---|---|---|---|---|---|---|')
        for div in divergences:
            detail = ', '.join(
                f'{src}={format_value(val)}'
                for src, val in sorted(div['values'].items(), key=lambda kv: kv[1])
            )
            lines.append(
                f'| {div["ticker"]} '
                f'| {div["metric"]} '
                f'| {format_value(div["min_value"])} ({div["min_source"]}) '
                f'| {format_value(div["max_value"])} ({div["max_source"]}) '
                f'| {div["spread"]:.0%} '
                f'| {detail} '
                f'| ☐ |'
            )
    lines.append('')

    return '\n'.join(lines)


def write_report(folder_output: str, content: str) -> str:
    path_folder = os.path.join(folder_output, 'arbiter')
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)

    output_file = os.path.join(path_folder, 'report.md')
    with open(output_file, 'w') as fd:
        fd.write(content)

    logging.info(f'📥 Report written to {output_file}')
    return output_file


def run_arbiter(folder_output: str, threshold: float) -> None:
    logging.info('===== ARBITER START =====')

    by_ticker, sources = aggregate_sources(folder_output)

    collisions = detect_identity_collisions(by_ticker)
    divergences = detect_value_divergences(by_ticker, threshold)
    logging.info(
        f'🔎 {len(collisions)} identity collision(s), '
        f'{len(divergences)} value divergence(s)'
    )

    content = render_report(by_ticker, sources, collisions, divergences, threshold)
    write_report(folder_output, content)

    logging.info('===== ARBITER END =====')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config', '-c',
        default='config.json'
    )
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=0.10
    )
    args = parser.parse_args()

    project_config = Config(args.config)

    initialize_logger(project_config.log)

    logging.info('🚀 Start arbiter!')
    try:
        run_arbiter(project_config.folder_output, args.threshold)
    except Exception as err:
        logging.exception(f'💥 Unhandled exception: {err}')
else:
    print('USAGE\npython3 arbiter.py')
