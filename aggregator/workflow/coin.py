import time
import logging

from config import Config
from api import (
    BinanceAPI,
    CoinGeckoAPI,
    CoinPaprikaAPI,
    CoinMarketCapAPI,
    CoinCapAPI,
    MessariAPI,
    CryptoCompareAPI,
    HashrateNoAPI,
    MinerStatAPI,
    WhatToMineAPI
)
from common import (
    Coin,
    CoinManager,
    HardwareManager,
    ApiHistoryManager,
    update_coin_by_binance,
    update_coin_by_what_to_mine,
    update_coin_by_hashrate_no,
    update_coin_by_minerstat,
    update_coin_by_coingecko
)


def workflow_coin_binance(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW BINANCE COIN =====')

    ###########################################################################
    if not config.apis.binance:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    symbol_prefix_skip = ['nicehash-', 'ausdt', 'usdt']
    api = BinanceAPI(config.apis.binance, config.folder_output)

    ###########################################################################
    try:
        ###########################################################################
        logging.info('🔄 get list coins...')
        symbols = api.get_symbols()

        ###########################################################################
        logging.info('🔄 filter coins...')
        filtered = []
        for symbol_data in symbols:
            symbol = symbol_data['symbol'].lower()
            if any(item in symbol for item in symbol_prefix_skip):
                continue
            if not symbol.endswith('usd'):
                continue
            if symbol != (symbol_data['baseAsset'] + 'usd').lower():
                continue
            filtered.append(symbol_data)

        ###########################################################################
        logging.info('🔄 update coins price...')
        logging.info(f'🔄 filtered symbols: {len(filtered)}')
        for data in filtered:
            symbol = data['symbol']
            tag = data['baseAsset'].lower().replace('usd', '')
            raw = api.get_price(symbol)
            if 'price' not in raw:
                logging.error(f'❌ missing key "price" -> {raw}')
                return
            coin = coin_manager.get_from_tag(tag)
            if coin:
                update_coin_by_binance(coin, raw)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('binance', success, int(duration * 1000), message)


def workflow_coin_coingecko(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW COINGECKO COIN =====')

    ###########################################################################
    if not config.apis.coingecko:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = CoinGeckoAPI(config.apis.coingecko, config.folder_output)

    ###########################################################################
    try:
        ###########################################################################
        logging.info('🔄 get list coins...')
        coins_list = api.get_coins_list()
        symbol_to_id = {c['symbol'].lower(): c['id'] for c in coins_list}

        ###########################################################################
        logging.info('🔄 collect coins to enrich...')
        ids_to_fetch = []
        for tag, cg_id in symbol_to_id.items():
            if coin_manager.get_from_tag(tag):
                ids_to_fetch.append(cg_id)

        if not ids_to_fetch:
            return

        ###########################################################################
        logging.info('🔄 get prices...')
        prices = api.get_price(','.join(ids_to_fetch))

        ###########################################################################
        logging.info('🔄 update coins price...')
        for tag, cg_id in symbol_to_id.items():
            if cg_id not in prices:
                continue
            usd = prices[cg_id].get('usd')
            if not usd:
                continue
            coin = coin_manager.get_from_tag(tag)
            if coin:
                update_coin_by_coingecko(coin, usd)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('coingecko', success, int(duration * 1000), message)


def workflow_coin_hashrate_no(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW HASHRATE NO COIN =====')

    ###########################################################################
    if not config.apis.hashrate_no:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = HashrateNoAPI(config.apis.hashrate_no, config.folder_output)

    ###########################################################################
    try:
        ###########################################################################
        logging.info('🔄 get coins informations....')
        coins = api.get_coins()
        if coins:
            for _, value in coins.items():
                tag = value['ticker'].lower()
                name = value['name'].lower()

                if not tag or tag == 'nicehash' or 'nicehash' in name:
                    continue

                coin = coin_manager.get_from_tag(tag)
                if coin is None:
                    coin = Coin()
                    coin.set_tag(tag, True)
                    coin.set_name(name, True)
                    coin_manager.insert(coin)

                update_coin_by_hashrate_no(coin, value)
        else:
            message = 'API returned empty response'

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('hashrate_no', success, int(duration * 1000), message)


def workflow_coin_miner_stat(config: Config, coin_manager: CoinManager, hardware_manager: HardwareManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW MINERSTAT COIN =====')

    ###########################################################################
    if not config.apis.minerstat:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = MinerStatAPI(config.apis.minerstat, config.folder_output)

    ###########################################################################
    try:
        #######################################################################
        logging.info('🔄 get coins informations....')
        coins = api.get_coins()
        for value in coins:
            if value['type'] != 'coin':
                continue
            tag = value['coin'].lower()
            coin = coin_manager.get_from_tag(tag)
            if coin:
                update_coin_by_minerstat(coin, value)

        #######################################################################
        logging.info('🔄 get hardware informations....')
        hardwares = api.get_hardware()
        for hardware in hardwares:
            hardware_type = hardware['type']
            if hardware_type != 'gpu':
                continue
            algorithms = hardware['algorithms']
            if not algorithms:
                continue
            hardware_name = hardware['name'].lower().replace(' ', '_')
            hardware_brand = hardware['brand'].lower()

            ###################################################################
            for algo_name, data in algorithms.items():
                algo_name = algo_name.lower().replace('-', '')
                speed = data['speed']
                power = data['power']
                hardware_manager.insert(
                    name=hardware_name,
                    brand=hardware_brand,
                    algo=algo_name,
                    speed=speed,
                    power=power)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('minerstat_coin', success, int(duration * 1000), message)


def workflow_coin_what_to_mine(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW WHAT TO MINE COIN =====')

    ###########################################################################
    if not config.apis.what_to_mine:
        logging.info('Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    logging.info('🔄 get coins informations....')
    api = WhatToMineAPI(config.apis.what_to_mine, config.folder_output)

    ###########################################################################
    try:
        coins = api.get_coins()
        for name, value in coins.items():
            tag = value['tag'].lower()
            name = name.lower()

            if tag == 'nicehash' or 'nicehash' in name:
                continue

            # Skip coins
            if tag in ('epic'):
                continue

            # skip coin without name
            if not name:
                continue

            coin = coin_manager.get_from_tag(tag)
            if coin is None:
                coin = Coin()
                coin.set_tag(tag, True)
                coin.set_name(name, True)
                coin_manager.insert(coin)

            coin.set_name(name, True)

            update_coin_by_what_to_mine(coin, value)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('what_to_mine', success, int(duration * 1000), message)


def workflow_coin_coinpaprika(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW COINPAPRIKA COIN =====')

    ###########################################################################
    if not config.apis.coinpaprika:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = CoinPaprikaAPI(config.apis.coinpaprika, config.folder_output)

    ###########################################################################
    try:
        logging.info('🔄 get tickers...')
        tickers = api.get_tickers()

        logging.info('🔄 collecting market data...')
        for entry in tickers:
            symbol = entry['symbol'].lower()

            # skip coins
            if symbol in ('cap', 'beam', 'cfx', 'epic', 'geod',
                          'prl'):
                continue

            coin = coin_manager.get_from_tag(symbol)
            if coin is None:
                # skip coin so many coins are not in our list
                continue

            quotes = entry['quotes']['USD']
            usd = quotes['price']
            market_cap = quotes['market_cap']

            coin.reward.set_market_cap(market_cap, True)
            coin.reward.set_usd(usd, True)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('coinpaprika', success, int(duration * 1000), message)


def workflow_coin_coinmarketcap(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW COINMARKETCAP COIN =====')

    ###########################################################################
    if not config.apis.coinmarketcap:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = CoinMarketCapAPI(config.apis.coinmarketcap, config.folder_output)

    ###########################################################################
    try:
        logging.info('🔄 get listings...')
        listings = api.get_listings()

        logging.info('🔄 collecting market data...')
        for entry in listings['data']:
            symbol = entry['symbol'].lower()

            coin = coin_manager.get_from_tag(symbol)
            if coin is None:
                # skip coin so many coins are not in our list
                continue

            quote = entry['quote']['USD']
            usd = quote['price']
            market_cap = quote['market_cap']

            coin.reward.set_market_cap(market_cap, True)
            coin.reward.set_usd(usd, True)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('coinmarketcap', success, int(duration * 1000), message)


def workflow_coin_coincap(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW COINCAP COIN =====')

    ###########################################################################
    if not config.apis.coincap:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = CoinCapAPI(config.apis.coincap, config.folder_output)

    ###########################################################################
    try:
        logging.info('🔄 get assets...')
        assets = api.get_assets()

        logging.info('🔄 collecting market data...')
        for entry in assets['data']:
            symbol = entry['symbol'].lower()

            coin = coin_manager.get_from_tag(symbol)
            if coin is None:
                # skip coin so many coins are not in our list
                continue

            # CoinCap returns numbers as strings, and market cap may be null
            usd = entry['priceUsd']
            market_cap = entry['marketCapUsd']

            if usd:
                coin.reward.set_usd(float(usd), True)
            if market_cap:
                coin.reward.set_market_cap(float(market_cap), True)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('coincap', success, int(duration * 1000), message)


def workflow_coin_messari(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW MESSARI COIN =====')

    ###########################################################################
    if not config.apis.messari:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = MessariAPI(config.apis.messari, config.folder_output)

    ###########################################################################
    try:
        logging.info('🔄 get assets...')
        assets = api.get_assets()

        logging.info('🔄 collecting market data...')
        for entry in assets['data']:
            symbol = entry['symbol'].lower()

            coin = coin_manager.get_from_tag(symbol)
            if coin is None:
                # skip coin so many coins are not in our list
                continue

            metrics = entry['metrics']
            usd = metrics['market_data']['price_usd']
            market_cap = metrics['marketcap']['current_marketcap_usd']

            if usd:
                coin.reward.set_usd(float(usd), True)
            if market_cap:
                coin.reward.set_market_cap(float(market_cap), True)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('messari', success, int(duration * 1000), message)


def workflow_coin_cryptocompare(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW CRYPTOCOMPARE COIN =====')

    ###########################################################################
    if not config.apis.cryptocompare:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    api = CryptoCompareAPI(config.apis.cryptocompare, config.folder_output)

    ###########################################################################
    try:
        # CryptoCompare expects an explicit symbol list, so only request the
        # coins we already track (and cap the batch to keep the URL sane).
        logging.info('🔄 collect coins to enrich...')
        tags = [coin.tag.upper() for coin in coin_manager.get_all() if coin.tag]
        tags = tags[:300]
        if not tags:
            return

        logging.info('🔄 get prices...')
        prices = api.get_prices(','.join(tags))

        logging.info('🔄 collecting market data...')
        for symbol, quotes in prices['RAW'].items():
            symbol = symbol.lower()

            coin = coin_manager.get_from_tag(symbol)
            if coin is None:
                # skip coin so many coins are not in our list
                continue

            usd = quotes['USD']['PRICE']
            market_cap = quotes['USD']['MKTCAP']

            coin.reward.set_market_cap(market_cap, True)
            coin.reward.set_usd(usd, True)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('cryptocompare', success, int(duration * 1000), message)
