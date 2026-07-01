import time
import logging

from config import Config
from api.explorer import (
    ErgoExplorerAPI,
    KaspaExplorerAPI,
    RavencoinRPCAPI,
    MoneroExplorerAPI,
    ConfluxExplorerAPI,
    ETCExplorerAPI,
    MempoolExplorerAPI,
    BlockchairExplorerAPI,
    EIquidusExplorerAPI,
    NervosExplorerAPI,
    SalviumExplorerAPI,
    QRLExplorerAPI,
    AlephiumExplorerAPI,
    WhatsOnChainAPI,
    PirateExplorerAPI
)
from common import (
    CoinManager,
    ApiHistoryManager,
    update_coin_by_explorer
)


def workflow_explorer_ergo(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER ERGO =====')

    ###########################################################################
    if 'erg' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['erg']
    api = ErgoExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'ergo')

    ###########################################################################
    try:
        logging.info('🔄 get ergo info...')
        raw = api.get_info()
        if not raw:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('ergo', 'erg')

        network_hashrate = raw.get('networkHashrate')
        difficulty = raw.get('difficulty')
        block_height = raw.get('fullHeight')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_ergo', success, int(duration * 1000), message)


def workflow_explorer_kaspa(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER KASPA =====')

    ###########################################################################
    if 'kas' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['kas']
    api = KaspaExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'kaspa')

    ###########################################################################
    try:
        logging.info('🔄 get kaspa info...')
        hashrate_info = api.get_hashrate()
        blockdag_info = api.get_blockdag()
        if not hashrate_info or not blockdag_info:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('kaspa', 'kas')

        _hashrate_ghs = hashrate_info.get('hashrate')
        network_hashrate = float(_hashrate_ghs) * 1e9 if _hashrate_ghs is not None else None
        difficulty = blockdag_info.get('difficulty')
        block_height = blockdag_info.get('virtualDaaScore')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_kaspa', success, int(duration * 1000), message)


def workflow_explorer_rvn(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER RVN =====')

    ###########################################################################
    if 'rvn' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['rvn']
    api = RavencoinRPCAPI(cfg.host, cfg.use_api, cfg.rpc_user, cfg.rpc_password, config.folder_output)

    ###########################################################################
    try:
        logging.info('🔄 get ravencoin blockchain info...')
        blockchain_info = api.get_blockchain_info()
        network_hashrate = api.get_network_hashrate()
        if not blockchain_info:
            message = 'RPC returned empty response'
            return

        coin = coin_manager.get_or_create('ravencoin', 'rvn')

        difficulty = blockchain_info.get('difficulty')
        block_height = blockchain_info.get('blocks')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_rvn', success, int(duration * 1000), message)


def workflow_explorer_xmr(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER XMR =====')

    ###########################################################################
    if 'xmr' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['xmr']
    api = MoneroExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'xmr')

    ###########################################################################
    try:
        logging.info('🔄 get monero stats...')
        raw = api.get_stats()
        if not raw:
            message = 'API returned empty response'
            return

        data = raw.get('data', {})
        coin = coin_manager.get_or_create('monero', 'xmr')

        network_hashrate = data.get('hash_rate')
        difficulty = data.get('difficulty')
        block_height = data.get('height')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_xmr', success, int(duration * 1000), message)


def workflow_explorer_cfx(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER CFX =====')

    ###########################################################################
    if 'cfx' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['cfx']
    api = ConfluxExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'cfx')

    ###########################################################################
    try:
        logging.info('🔄 get conflux stats...')
        raw = api.get_stats()
        if not raw:
            message = 'API returned empty response'
            return

        data_list = raw.get('data', {}).get('list', [])
        if not data_list:
            message = 'API returned empty list'
            return

        latest = data_list[0]
        coin = coin_manager.get_or_create('conflux', 'cfx')

        network_hashrate = latest.get('hashRate')
        difficulty = latest.get('difficulty')
        block_height = None

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_cfx', success, int(duration * 1000), message)


def workflow_explorer_etc(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER ETC =====')

    ###########################################################################
    if 'etc' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['etc']
    api = ETCExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'etc')

    ###########################################################################
    try:
        logging.info('🔄 get etc stats...')
        raw = api.get_stats()
        if not raw:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('ethereum classic', 'etc')

        network_hashrate = raw.get('network_hashrate')
        difficulty = raw.get('difficulty')
        block_height = raw.get('total_blocks')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_etc', success, int(duration * 1000), message)


def workflow_explorer_mempool(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager,
    tag: str,
    name: str
) -> None:
    """Generic mempool.space-family explorer (btc, ltc, fb)."""
    logging.info(f'===== WORKFLOW EXPLORER MEMPOOL {tag.upper()} =====')

    ###########################################################################
    if tag not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer[tag]
    api = MempoolExplorerAPI(cfg.host, cfg.use_api, config.folder_output, tag)

    ###########################################################################
    try:
        logging.info(f'🔄 get {tag} mempool hashrate...')
        raw = api.get_hashrate()
        if not raw:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create(name, tag)

        network_hashrate = raw.get('currentHashrate')
        difficulty = raw.get('currentDifficulty')

        update_coin_by_explorer(coin, network_hashrate, difficulty, None)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add(f'explorer_{tag}', success, int(duration * 1000), message)


def workflow_explorer_blockchair(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager,
    tag: str,
    name: str
) -> None:
    """Generic Blockchair explorer (bch, doge, dash, zec, xec)."""
    logging.info(f'===== WORKFLOW EXPLORER BLOCKCHAIR {tag.upper()} =====')

    ###########################################################################
    if tag not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer[tag]
    api = BlockchairExplorerAPI(cfg.host, cfg.use_api, config.folder_output, tag)

    ###########################################################################
    try:
        logging.info(f'🔄 get {tag} blockchair stats...')
        raw = api.get_stats()
        data = raw.get('data', {})
        if not data:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create(name, tag)

        network_hashrate = data.get('hashrate_24h')
        difficulty = data.get('difficulty')
        block_height = data.get('blocks')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add(f'explorer_{tag}', success, int(duration * 1000), message)


def workflow_explorer_eiquidus(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager,
    tag: str,
    name: str
) -> None:
    """Generic eIquidus explorer (dingo, pep, rxd)."""
    logging.info(f'===== WORKFLOW EXPLORER EIQUIDUS {tag.upper()} =====')

    ###########################################################################
    if tag not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer[tag]
    api = EIquidusExplorerAPI(cfg.host, cfg.use_api, config.folder_output, tag)

    ###########################################################################
    try:
        logging.info(f'🔄 get {tag} eiquidus difficulty/hashrate...')
        difficulty = api.get_difficulty()
        network_hashrate = api.get_network_hashrate()

        coin = coin_manager.get_or_create(name, tag)

        update_coin_by_explorer(coin, network_hashrate, difficulty, None)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add(f'explorer_{tag}', success, int(duration * 1000), message)


def workflow_explorer_ckb(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER CKB =====')

    ###########################################################################
    if 'ckb' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['ckb']
    api = NervosExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'ckb')

    ###########################################################################
    try:
        logging.info('🔄 get nervos statistics...')
        raw = api.get_statistics()
        attributes = raw.get('data', {}).get('attributes', {})
        if not attributes:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('nervos network', 'ckb')

        network_hashrate = attributes.get('hash_rate')
        difficulty = attributes.get('current_epoch_difficulty')

        update_coin_by_explorer(coin, network_hashrate, difficulty, None)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_ckb', success, int(duration * 1000), message)


def workflow_explorer_sal(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER SAL =====')

    ###########################################################################
    if 'sal' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['sal']
    api = SalviumExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'sal')

    ###########################################################################
    try:
        logging.info('🔄 get salvium network info...')
        raw = api.get_network_info()
        data = raw.get('data', {})
        if not data:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('salvium', 'sal')

        network_hashrate = data.get('hash_rate')
        difficulty = data.get('difficulty')
        block_height = data.get('height')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_sal', success, int(duration * 1000), message)


def workflow_explorer_qrl(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER QRL =====')

    ###########################################################################
    if 'qrl' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['qrl']
    api = QRLExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'qrl')

    ###########################################################################
    try:
        logging.info('🔄 get qrl mining stats...')
        raw = api.get_mining_stats()
        if not raw:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('quantum resistant ledger', 'qrl')

        network_hashrate = raw.get('hashrate')
        difficulty = raw.get('difficulty')
        block_height = raw.get('block_number')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_qrl', success, int(duration * 1000), message)


def workflow_explorer_alph(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER ALPH =====')

    ###########################################################################
    if 'alph' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['alph']
    api = AlephiumExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'alph')

    ###########################################################################
    try:
        logging.info('🔄 get alephium hashrates...')
        to_ts = int(time.time() * 1000)
        from_ts = to_ts - 24 * 3600 * 1000
        raw = api.get_hashrates(from_ts, to_ts)
        if not raw:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('alephium', 'alph')

        # The backend exposes no difficulty endpoint; difficulty stays on the
        # hashrate.no fallback. Take the most recent hashrate sample.
        last = raw[-1]
        network_hashrate = last.get('hashrate') if isinstance(last, dict) else last[1]

        update_coin_by_explorer(coin, network_hashrate, None, None)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_alph', success, int(duration * 1000), message)


def workflow_explorer_bsv(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER BSV =====')

    ###########################################################################
    if 'bsv' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['bsv']
    api = WhatsOnChainAPI(cfg.host, cfg.use_api, config.folder_output, 'bsv')

    ###########################################################################
    try:
        logging.info('🔄 get bitcoin sv chain info...')
        raw = api.get_chain_info()
        difficulty = raw.get('difficulty')
        if not difficulty:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('bitcoin sv', 'bsv')

        # WhatsOnChain exposes no hashrate; derive it from difficulty (SHA-256, 600s block time).
        network_hashrate = float(difficulty) * (2 ** 32) / 600.0
        block_height = raw.get('blocks')

        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_bsv', success, int(duration * 1000), message)


def workflow_explorer_arrr(
    config: Config,
    coin_manager: CoinManager,
    api_history_manager: ApiHistoryManager
) -> None:
    logging.info('===== WORKFLOW EXPLORER ARRR =====')

    ###########################################################################
    if 'arrr' not in config.apis.explorer:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = True
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['arrr']
    api = PirateExplorerAPI(cfg.host, cfg.use_api, config.folder_output, 'arrr')

    ###########################################################################
    try:
        logging.info('🔄 get pirate chain difficulty...')
        raw = api.get_difficulty()
        difficulty = raw.get('difficulty')
        if not difficulty:
            message = 'API returned empty response'
            return

        coin = coin_manager.get_or_create('pirate chain', 'arrr')

        # Equihash Sol/s hashrate is not exposed — it stays on the hashrate.no fallback.
        update_coin_by_explorer(coin, None, difficulty, None)

    ###########################################################################
    except Exception as err:
        success = False
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_arrr', success, int(duration * 1000), message)
