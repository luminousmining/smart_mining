#include <boost/json.hpp>

#include <common/log/log.hpp>
#include <network/session/session.hpp>


void network::session::Session::onPoolRequest(stratum::PoolRequest const& request)
{
    stratum::MinerRequest body
    {
        .id = request.id,
        .method = request.method,
        .params = request.params
    };
    sendToMiner(body.to_json());
}


void network::session::Session::onPoolResponse(stratum::Response const& response)
{
    switch (response.id)
    {
        case stratum::STRATUM_ID_SUBSCRIBE:
        {
            onMiningSubscribe(response);
            break;
        }
        case stratum::STRATUM_ID_AUTHORIZE:
        {
            onMiningAuthorized(response);
            break;
        }
        default:
        {
            // TODO: MINER_LOGGED
            stratum::Response body
            {
                .id = response.id,
                .error = response.error,
                .result = response.result
            };
            sendToMiner(body.to_json());
        }
    }
}


void network::session::Session::onMiningSubscribe(stratum::Response const& response)
{
    try
    {
        if (!response.result.is_array())
        {
            logMinerErr() << "result is not an array!";
            return;
        }
        poolData.extranonce = response.result.as_array().at(1).as_string();
        
        logMinerInfo() << "subscribed from pool " << poolData.fullname;

        if (false == sendPoolAuthorize())
        {
            return;
        }
    }
    catch (boost::system::system_error const& e)
    {
        logMinerErr()
            << "fail to parse Result "
            << boost::json::serialize(response.result)
            << " => " << e.what();
    }
}


void network::session::Session::onMiningAuthorized(stratum::Response const& response)
{
    if (false == response.error.is_null())
    {
        // TODO: CHANGE_POOL
        logMinerInfo() << "unauthorized from pool " << poolData.fullname;
        minerData.logged = false;
        return;
    }

    bool const error{ response.result.as_bool() };
    if (false ==  error)
    {
        // TODO: CHANGE_POOL
        logMinerInfo() << "unauthorized from pool " << poolData.fullname;
        minerData.logged = false;
        return;
    }

    logMinerInfo() << "authorized from pool " << poolData.fullname;
    minerData.logged = true;

    if (   currentCoin.algorithm == "ethash"
        || currentCoin.algorithm == "kawpow")
    {
        if (poolData.extranonce.size() < 2)
        {
            logMinerErr() << "wrong size[" << poolData.extranonce.size() << "] extranonce!";
            return;
        }

        if (false == sendSmartMiningSetAlgorithm())
        {
            return;
        }
        if (false == sendSmartMiningSetExtranonce(poolData.extranonce))
        {
            return;
        }
    } 
    else if (currentCoin.algorithm == "autolykosv2")
    {
        if (poolData.extranonce.size() < 3)
        {
            logMinerErr() << "wrong size[" << poolData.extranonce.size() << "] extranonce!";
            return;
        }
        
        sendSmartMiningSetExtranonce2(poolData.extranonce, poolData.extranonce2);
    }
    else
    {
        logMinerInfo() << "cannot mine with algorithm [" << currentCoin.algorithm << "] unimplemented!";
    }
}
