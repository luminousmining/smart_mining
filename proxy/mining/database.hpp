#pragma once

#include <string>
#include <vector>

#include <boost/thread/mutex.hpp>

#include <mining/coin_table.hpp>
#include <profile/data_emission.hpp>
#include <profile/data_hash_usd.hpp>
#include <profile/data_market_cap.hpp>
#include <profile/data_network_hashrate.hpp>
#include <profile/data_usd_sec.hpp>


namespace mining
{
    class Database
    {
    public:
        std::vector<mining::CoinTable>                   coins{};
        std::vector<profile::ProfileDataEmission>        profileEmission{};
        std::vector<profile::ProfileDataHashUsd>         profileHashUsd{};
        std::vector<profile::ProfileDataUsdSec>          profileUsdSec{};
        std::vector<profile::ProfileDataMarketcap>       profileMarketCap{};
        std::vector<profile::ProfileDataNetworkHashrate> profileNetworkHasrateGreater{};
        std::vector<profile::ProfileDataNetworkHashrate> profileNetworkHasrateLess{};

        bool reload();
        std::string getBestCoin(std::vector<std::string> const& listCoinMiner) const;
        std::string getAlgorithm(std::string const& tag) const;

    private:
        boost::mutex locker{};

        void reloadBaseCoin();
        void reloadProfileEmission();
        void reloadProfileHashUsd();
        void reloadProfileUsdSec();
        void reloadProfileMarketCap();
        void reloadProfileNetworkHashrate();
    };
}
