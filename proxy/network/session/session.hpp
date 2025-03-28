#pragma once

#include <string>

#include <boost/function.hpp>
#include <boost/json.hpp>
#include <boost/thread.hpp>
#include <boost/thread/mutex.hpp>

#include <mining/database.hpp>
#include <network/client_tcp.hpp>
#include <network/stream.hpp>
#include <network/session/miner_data.hpp>
#include <network/session/pool_data.hpp>
#include <profile/profile_manager.hpp>
#include <stratum/stratum.hpp>
#include <stratum/miner.hpp>
#include <stratum/proxy.hpp>
#include <stratum/pool.hpp>


namespace network
{
    namespace session
    {
        struct Session
        {
        public:
            // Common
            bool                        alive{ false };
            network::session::MinerData minerData{};
            network::session::PoolData  poolData{};
            mining::CoinMiner           currentCoin{};
            mining::Database*           database{ nullptr };
            profile::ProfileManager*    profileManager{ nullptr };

            // Finance
            bool switchCoin(std::string const& coinTag);

            // common
            void run();
            bool isAlive() const;
            bool isLogged(std::string const& functionName) const;

            // stream
            bool connectToPool();
            void closeStreamMiner();
            void closeStreamPool();
            void shutdown();
            bool sendToMiner(boost::json::value const& request);
            bool sendToPool(boost::json::value const& request);

            // Miner Sesssion
            void receivePacketMiner();
            void executeMinerRPC(std::string const& rpc);
            void onMethodMiner(stratum::MinerRequest const& minerRequest);
            void onSubscribeMiner(int64_t const id,
                                  boost::json::value const& params);
            void onSubmitMiner(int64_t id,
                               std::string const& method,
                               boost::json::value const& params);
            void onSmartMiningSetProfile(int64_t const id,
                                         boost::json::value const& params);
            bool sendSmartMiningSetAlgorithm();
            bool sendSmartMiningSetExtranonce(std::string const& extraNonce);
            bool sendSmartMiningSetExtranonce2(std::string const& extraNonce,
                                        int32_t const extranonceSize);

            // Pool Session
            void receivePacketPool();
            void executePoolRPC(std::string const& rpc);
            void onPoolRequest(stratum::PoolRequest const& request);
            void onPoolResponse(stratum::Response const& response);
            void onMiningSubscribe(stratum::Response const& response);
            void onMiningAuthorized(stratum::Response const& response);
            bool sendPoolSubscribe();
            bool sendPoolAuthorize();

        private:
            void onReceivePacketMiner(boost::system::error_code const& ec, size_t bytes);
            void onReceivePacketPool(boost::system::error_code const& ec, size_t bytes);
        };
    }
}
