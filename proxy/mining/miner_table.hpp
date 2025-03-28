#pragma once

#include <string>
#include <vector>
#include <mutex>
#include <memory>

#include <mining/coin_miner.hpp>


namespace mining
{
    struct MinerTable
    {
        std::vector<mining::CoinMiner> listCoin{};
        std::string                    workerName{};
        std::string                    password{};

        MinerTable() = default;
        ~MinerTable() = default;

        MinerTable(MinerTable const&) = delete;
        MinerTable& operator=(MinerTable const&) = delete;
        MinerTable(MinerTable&&) = default;
        MinerTable& operator=(MinerTable&&) = default;

        bool containsCoin(std::string const& tag) const;
        mining::CoinMiner getCoinMiner(std::string const& coinTag);
        void addCoinMinable(std::string const& coin,
                            std::string const& algorithm,
                            std::string const& poolUrl,
                            uint32_t const port,
                            std::string const& wallet);
    };
}
