#pragma once

#include <string>
#include <vector>

#include <profile/data_emission.hpp>
#include <profile/data_hash_usd.hpp>
#include <profile/data_market_cap.hpp>
#include <profile/data_network_hashrate.hpp>
#include <profile/data_usd_sec.hpp>
#include <mining/miner_table.hpp>


namespace profile
{
    struct ProfileManager
    {
    public:
        std::string findBestCoin(mining::MinerTable const& table,
                                 std::vector<profile::ProfileDataEmission> const& profile);
        std::string findBestCoin(mining::MinerTable const& table,
                                 std::vector<profile::ProfileDataUsdSec> const& profile);
        std::string findBestCoin(mining::MinerTable const& table,
                                 std::vector<profile::ProfileDataMarketcap> const& profile);
        std::string findBestCoin(mining::MinerTable const& table,
                                 std::vector<profile::ProfileDataNetworkHashrate> const& profile);
        std::string findBestCoin(mining::MinerTable const& table,
                                 std::vector<profile::ProfileDataHashUsd> const& profile);
    };
}
