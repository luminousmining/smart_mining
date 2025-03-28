#pragma once

#include <string>

#include <boost/json.hpp>


namespace mining
{
    constexpr char API_HOST[]{ "localhost" };
    constexpr char API_PORT[]{ "3000" };
    constexpr char API_KEY[]{ "123456" };
    constexpr uint32_t API_VERSION_HTTP{ 11u };

    std::string apiParamApiKey();
    boost::json::value apiGet(std::string const& endpoint);
    boost::json::array apiInfoCoins();
    boost::json::object apiInfoCoin(std::string const& tag);
    boost::json::array apiProfileEmission();
    boost::json::array apiProfileHashUsd();
    boost::json::array apiProfileUsdSec();
    boost::json::array apiProfileMarketCap();
    boost::json::array apiProfileNetworkHashrate(bool const greater);
}
