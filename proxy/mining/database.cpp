#include <algorithm>

#include <boost/algorithm/string.hpp>

#include <common/log/log.hpp>
#include <common/boost_utils.hpp>
#include <common/custom.hpp>
#include <mining/api.hpp>
#include <mining/database.hpp>


bool mining::Database::reload()
{
    UNIQUE_LOCK(locker);

    logInfo() << "Reloading Database...";

    reloadBaseCoin();
    reloadProfileEmission();
    reloadProfileUsdSec();
    reloadProfileMarketCap();
    reloadProfileNetworkHashrate();

    return true;
}


void mining::Database::reloadBaseCoin()
{
    boost::json::array data(mining::apiInfoCoins());

    coins.clear();

    for (auto value : data)
    {
        boost::json::object coin{ value.as_object() };

        mining::CoinTable table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.algorithm = boost::algorithm::to_lower_copy(common::boostGetString(coin, "algorithm"));
        table.usd = common::boostJsonGetNumber<double>(coin.at("usd"));
        table.usdSec = common::boostJsonGetNumber<double>(coin.at("usd_sec"));
        table.difficulty = common::boostJsonGetNumber<double>(coin.at("difficulty"));
        table.networkHashrate = common::boostJsonGetNumber<double>(coin.at("network_hashrate"));
        table.emissionCoin = common::boostJsonGetNumber<double>(coin.at("emission_coin"));
        table.emissionUsd = common::boostJsonGetNumber<double>(coin.at("emission_usd"));

        coins.emplace_back(table);
    }
}


void mining::Database::reloadProfileEmission()
{
    boost::json::array data(mining::apiProfileEmission());

    profileEmission.clear();

    for (auto value : data)
    {
        boost::json::object coin{ value.as_object() };

        profile::ProfileDataEmission table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.emissionUsd = common::boostJsonGetNumber<double>(coin.at("emission_usd"));

        profileEmission.emplace_back(table);
    }
}


void mining::Database::reloadProfileHashUsd()
{
    boost::json::array data(mining::apiProfileHashUsd());

    profileHashUsd.clear();

    for (auto value : data)
    {
        boost::json::object coin{ value.as_object() };

        profile::ProfileDataHashUsd table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.hashUsd = common::boostJsonGetNumber<double>(coin.at("hash_usd"));

        profileHashUsd.emplace_back(table);
    }
}


void mining::Database::reloadProfileUsdSec()
{
    boost::json::array data(mining::apiProfileUsdSec());

    profileUsdSec.clear();

    for (auto value : data)
    {
        boost::json::object coin{ value.as_object() };

        profile::ProfileDataUsdSec table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.usdSec = common::boostJsonGetNumber<double>(coin.at("usd_sec"));

        profileUsdSec.emplace_back(table);
    }
}


void mining::Database::reloadProfileMarketCap()
{
    boost::json::array data(mining::apiProfileMarketCap());

    profileMarketCap.clear();

    for (auto value : data)
    {
        boost::json::object coin{ value.as_object() };

        profile::ProfileDataMarketcap table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.marketCap = common::boostJsonGetNumber<double>(coin.at("market_cap"));

        profileMarketCap.emplace_back(table);
    }
}


void mining::Database::reloadProfileNetworkHashrate()
{
    ///////////////////////////////////////////////////////////////////////////
    boost::json::array dataGreater(mining::apiProfileNetworkHashrate(true));

    profileNetworkHasrateGreater.clear();

    for (auto value : dataGreater)
    {
        boost::json::object coin{ value.as_object() };

        profile::ProfileDataNetworkHashrate table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.networkHashrate = common::boostJsonGetNumber<double>(coin.at("network_hashrate"));

        profileNetworkHasrateGreater.emplace_back(table);
    }

    ///////////////////////////////////////////////////////////////////////////
    boost::json::array dataLess(mining::apiProfileNetworkHashrate(false));

    profileNetworkHasrateLess.clear();

    for (auto value : dataLess)
    {
        boost::json::object coin{ value.as_object() };

        profile::ProfileDataNetworkHashrate table{};

        table.name = boost::algorithm::to_lower_copy(common::boostGetString(coin, "name"));
        table.tag = boost::algorithm::to_upper_copy(common::boostGetString(coin, "tag"));
        table.networkHashrate = common::boostJsonGetNumber<double>(coin.at("network_hashrate"));

        profileNetworkHasrateLess.emplace_back(table);
    }
}


std::string mining::Database::getBestCoin(std::vector<std::string> const& listCoinMiner) const
{
    return coins.at(0).tag;
}


std::string mining::Database::getAlgorithm(std::string const& tag) const
{
    for (mining::CoinTable const& coin : coins)
    {
        if (coin.tag == tag)
        {
            return coin.algorithm;
        }
    }

    return "";
}
