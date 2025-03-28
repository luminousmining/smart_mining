#include <boost/json.hpp>

#include <network/session/session.hpp>


bool network::session::Session::sendPoolSubscribe()
{
    boost::json::array params
    {
        "luminousminer/0.1",
        "EthereumStratum/1.0.0"
    };
    stratum::PoolRequest request
    {
        .id = stratum::STRATUM_ID_SUBSCRIBE,
        .method = stratum::STRATUM_METHOD_MINING_SUBSCRIBE,
        .params = params
    };

    return sendToPool(request.to_json());
}


bool network::session::Session::sendPoolAuthorize()
{
    std::string worker{currentCoin.wallet + "." + minerData.table.workerName };

    boost::json::array params
    {
        worker,
        minerData.table.password
    };

    stratum::PoolRequest request
    {
        .id = stratum::STRATUM_ID_AUTHORIZE,
        .method = "mining.authorize",
        .params = params
    };

    return sendToPool(request.to_json());
}