#pragma once

#include <memory>
#include <vector>
#include <string>

#include <boost/thread.hpp>
#include <boost/thread/mutex.hpp>

#include <mining/database.hpp>
#include <network/stream.hpp>
#include <network/session/session.hpp>
#include <profile/profile_manager.hpp>


namespace network
{
    namespace session
    {
        struct SessionManager
        {
        public:
            boost::mutex                            locker{};
            std::vector<network::session::Session*> sessions{};
            mining::Database*                       database{ nullptr };
            profile::ProfileManager*                profileManager{ nullptr };

            bool createSession(network::IOStream* stream);
            void process();
            bool update();
            std::string onFindBestCoin(network::session::MinerData const& minerData);

        private:
            size_t getSessionCount() const;
        };
    }
}
