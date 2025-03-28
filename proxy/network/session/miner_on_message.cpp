#include <boost/algorithm/string.hpp>
#include <boost/exception/diagnostic_information.hpp>

#include <common/log/log.hpp>
#include <common/boost_utils.hpp>
#include <common/cast.hpp>
#include <common/custom.hpp>
#include <network/session/session.hpp>


void network::session::Session::onMethodMiner(stratum::MinerRequest const& minerRequest)
{
    if (minerRequest.method == stratum::STRATUM_METHOD_MINING_SUBSCRIBE)
    {
        onSubscribeMiner(minerRequest.id, minerRequest.params);
    }
    else if (minerRequest.method == stratum::STRATUM_METHOD_MINING_SUBMIT)
    {
        logInfo()
            << "Share found from [" << currentCoin.wallet
            << "] on pool[" << poolData.fullname << "]";

        onSubmitMiner(minerRequest.id, minerRequest.method, minerRequest.params);
    }
    else if (minerRequest.method == stratum::STRATUM_METHOD_SM_SET_PROFILE)
    {
        onSmartMiningSetProfile(minerRequest.id, minerRequest.params);
    }
    else
    {
        logErr()
            << "Unknown method[" << minerRequest.method
            << "] from miner[" << currentCoin.wallet
            << "] on pool[" << poolData.fullname << "]";
    }
}


void network::session::Session::onSubscribeMiner(
    int64_t id,
    boost::json::value const& params)
{
    // Check the ID
    if (id != stratum::STRATUM_ID_SUBSCRIBE)
    {
        stratum::Response response
        {
            .id = id,
            .error = true,
            .result = boost::json::value("SUBSCRIBE ID must be [" + std::to_string(stratum::STRATUM_ID_SUBSCRIBE) + "]!")
        };
        sendToMiner(response.to_json());
        return;
    }

    try
    {
        auto const& paramsArray{ params.as_array() };
        std::string workerName{  paramsArray.at(0).as_string().c_str() };
        std::string password{ paramsArray.at(1).as_string().c_str() };
        auto const& coins{ paramsArray.at(2).as_array() };

        // Create new user
        minerData.table.workerName = workerName;
        minerData.table.password = password;

        // Insert list of coin minage for this user
        for (auto item : coins)
        {
            auto const& itemArray{ item.as_array() };
            auto const size{ itemArray.size() };
            if (4 != size)
            {
                logErr() << "Len data must be 4";
                continue;
            }

            std::string const coin{ boost::algorithm::to_upper_copy(common::boostGetString(itemArray, 0)) };
            std::string const pool{ common::boostGetString(itemArray, 1) };
            uint32_t const port{ common::boostJsonGetNumber<uint32_t>(itemArray.at(2)) };
            std::string const wallet{ common::boostGetString(itemArray, 3) };

            std::string const algorithm{ database->getAlgorithm(coin) };

            minerData.table.addCoinMinable(coin, algorithm, pool, port, wallet);
        }
    }
    catch (boost::system::system_error const& e)
    {
        stratum::Response response
        {
            .id = id,
            .error = true,
            .result = e.what()
        };
        sendToMiner(response.to_json());
        return;
    }

    // Send response OK
    stratum::Response response
    { 
        .id = id,
        .error = false,
        .result = ""
    };
    sendToMiner(response.to_json());
}


void network::session::Session::onSubmitMiner(
    int64_t const id,
    std::string const& method,
    boost::json::value const& params)
{
    if (id < stratum::STRATUM_ID_SUBMIT_MINIMAL)
    {
        std::string message
        {
            "Minimal \"id\" should be [" + std::to_string(stratum::STRATUM_ID_SUBMIT_MINIMAL) + "]!"
        };
        stratum::Response response
        {
            .id = id,
            .error = true,
            .result = boost::json::value(message)
        };
        sendToMiner(response.to_json());
        return;
    }

    try
    {
        boost::json::array submitParams(params.as_array());

        std::string wallet{ currentCoin.wallet };
        std::string workerName{ minerData.table.workerName };

        if (true == wallet.empty() || true == workerName.empty())
        {
            logErr()
                << "pool[" << poolData.fullname
                << "] cannot send request! Wallet[" << wallet
                << "] WorkerName[" << workerName << "] empty!";
            return;
        }

        submitParams[0] = wallet + "." + workerName;

        stratum::MinerRequestPool request
        {
            .id = id,
            .method = method,
            .params = submitParams
        };
        sendToPool(request.to_json());
    }
    catch (boost::system::system_error const& e)
    {
        logErr() << e.what();
        stratum::Response response
        {
            .id = id,
            .error = true,
            .result = "JSON malformatted!"
        };
        sendToMiner(response.to_json());
    }
}


void network::session::Session::onSmartMiningSetProfile(
    int64_t const id,
    boost::json::value const& params)
{
    try
    {
        boost::json::array paramsArray(params.as_array());

        std::string const profileName{ common::boostGetString(paramsArray, 0) };

        std::string coinName;
        if (profileName == "emission")
        {
            coinName = profileManager->findBestCoin(minerData.table, database->profileEmission);
        }
        else if (profileName == "usd_sec")
        {
            coinName = profileManager->findBestCoin(minerData.table, database->profileUsdSec);
        }
        else if (profileName == "market_cap")
        {
            coinName = profileManager->findBestCoin(minerData.table, database->profileMarketCap);
        }
        else if (profileName == "network_hashrate_greater")
        {
            coinName = profileManager->findBestCoin(minerData.table, database->profileNetworkHasrateGreater);
        }
        else if (profileName == "network_hashrate_less")
        {
            coinName = profileManager->findBestCoin(minerData.table, database->profileNetworkHasrateLess);
        }
        else
        {
            logErr() << "Wrong profile sent!";
            stratum::Response response
            {
                .id = id,
                .error = true,
                .result = "Wrong profile sent!"
            };
            sendToMiner(response.to_json());
            return;
        }
        switchCoin(coinName);
    }
    catch(boost::system::system_error const& e)
    {
        logErr() << e.what();
        stratum::Response response
        {
            .id = id,
            .error = true,
            .result = "JSON malformatted!"
        };
        sendToMiner(response.to_json());
    }
}