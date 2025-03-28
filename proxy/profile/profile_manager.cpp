#include <common/log/log.hpp>
#include <profile/profile_manager.hpp>


std::string profile::ProfileManager::findBestCoin(
    mining::MinerTable const& table,
    std::vector<profile::ProfileDataEmission> const& profile)
{
    std::string lastTag{};
    double lastValue{ 0.0 };

    for (profile::ProfileDataEmission const& data : profile)
    {
        if (true == table.containsCoin(data.tag))
        {
            if (lastValue < data.emissionUsd)
            {
                lastValue = data.emissionUsd;
                lastTag = data.tag;
            }
        }
    }

    return lastTag;
}


std::string profile::ProfileManager::findBestCoin(
    mining::MinerTable const& table,
    std::vector<profile::ProfileDataUsdSec> const& profile)
{
    std::string lastTag{};
    double lastValue{ 0.0 };

    for (profile::ProfileDataUsdSec const& data : profile)
    {
        if (true == table.containsCoin(data.tag))
        {
            if (lastValue < data.usdSec)
            {
                lastValue = data.usdSec;
                lastTag = data.tag;
            }
        }
    }

    return lastTag;
}


std::string profile::ProfileManager::findBestCoin(
    mining::MinerTable const& table,
    std::vector<profile::ProfileDataMarketcap> const& profile)
{
    std::string lastTag{};
    double lastValue{ 0.0 };

    for (profile::ProfileDataMarketcap const& data : profile)
    {
        if (true == table.containsCoin(data.tag))
        {
            if (lastValue < data.marketCap)
            {
                lastValue = data.marketCap;
                lastTag = data.tag;
            }
        }
    }

    return lastTag;
}


std::string profile::ProfileManager::findBestCoin(
    mining::MinerTable const& table,
    std::vector<profile::ProfileDataNetworkHashrate> const& profile)
{
    std::string lastTag{};
    double lastValue{ 0.0 };

    for (profile::ProfileDataNetworkHashrate const& data : profile)
    {
        if (true == table.containsCoin(data.tag))
        {
            if (lastValue < data.networkHashrate)
            {
                lastValue = data.networkHashrate;
                lastTag = data.tag;
            }
        }
    }

    return lastTag;
}


std::string profile::ProfileManager::findBestCoin(
    mining::MinerTable const& table,
    std::vector<profile::ProfileDataHashUsd> const& profile)
{
    std::string lastTag{};
    double lastValue{ 0.0 };

    for (profile::ProfileDataHashUsd const& data : profile)
    {
        if (true == table.containsCoin(data.tag))
        {
            if (lastValue < data.hashUsd)
            {
                lastValue = data.hashUsd;
                lastTag = data.tag;
            }
        }
    }

    return lastTag;
}
