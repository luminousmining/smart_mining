import time
import logging

from config import Config
from api.explorer import (
    ErgoExplorerAPI,
    KaspaExplorerAPI,
    RavencoinRPCAPI,
    MoneroExplorerAPI,
    ConfluxExplorerAPI,
    ETCExplorerAPI
)
from common import (
    Coin,
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
    success = False
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

        coin = coin_manager.get_from_tag('erg')
        if coin is None:
            coin = Coin()
            coin.name = 'erg'
            coin.tag = 'erg'
            coin_manager.insert(coin)

        network_hashrate = raw.get('networkHashrate')
        difficulty       = raw.get('difficulty')
        block_height     = raw.get('fullHeight')
        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

        success = True

    ###########################################################################
    except Exception as err:
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
    success = False
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

        coin = coin_manager.get_from_tag('kas')
        if coin is None:
            coin = Coin()
            coin.name = 'kas'
            coin.tag = 'kas'
            coin_manager.insert(coin)

        _hashrate_ghs    = hashrate_info.get('hashrate')
        network_hashrate = float(_hashrate_ghs) * 1e9 if _hashrate_ghs is not None else None
        difficulty       = blockdag_info.get('difficulty')
        block_height     = blockdag_info.get('virtualDaaScore')
        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

        success = True

    ###########################################################################
    except Exception as err:
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
    success = False
    message = ''

    ###########################################################################
    cfg = config.apis.explorer['rvn']
    api = RavencoinRPCAPI(cfg.host, cfg.use_api, cfg.rpc_user, cfg.rpc_password, config.folder_output)

    ###########################################################################
    try:
        logging.info('🔄 get ravencoin blockchain info...')
        blockchain_info  = api.get_blockchain_info()
        network_hashrate = api.get_network_hashrate()
        if not blockchain_info:
            message = 'RPC returned empty response'
            return

        coin = coin_manager.get_from_tag('rvn')
        if coin is None:
            coin = Coin()
            coin.name = 'rvn'
            coin.tag = 'rvn'
            coin_manager.insert(coin)

        difficulty   = blockchain_info.get('difficulty')
        block_height = blockchain_info.get('blocks')
        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

        success = True

    ###########################################################################
    except Exception as err:
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
    success = False
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
        coin = coin_manager.get_from_tag('xmr')
        if coin is None:
            coin = Coin()
            coin.name = 'xmr'
            coin.tag = 'xmr'
            coin_manager.insert(coin)

        network_hashrate = data.get('hash_rate')
        difficulty       = data.get('difficulty')
        block_height     = data.get('height')
        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

        success = True

    ###########################################################################
    except Exception as err:
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
    success = False
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
        coin = coin_manager.get_from_tag('cfx')
        if coin is None:
            coin = Coin()
            coin.name = 'cfx'
            coin.tag = 'cfx'
            coin_manager.insert(coin)

        network_hashrate = latest.get('hashRate')
        difficulty       = latest.get('difficulty')
        block_height     = None
        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

        success = True

    ###########################################################################
    except Exception as err:
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
    success = False
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

        coin = coin_manager.get_from_tag('etc')
        if coin is None:
            coin = Coin()
            coin.name = 'etc'
            coin.tag = 'etc'
            coin_manager.insert(coin)

        network_hashrate = raw.get('network_hashrate')
        difficulty       = raw.get('difficulty')
        block_height     = raw.get('total_blocks')
        update_coin_by_explorer(coin, network_hashrate, difficulty, block_height)

        success = True

    ###########################################################################
    except Exception as err:
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('explorer_etc', success, int(duration * 1000), message)
