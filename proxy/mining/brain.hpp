#pragma once

#include <memory>
#include <chrono>

#include <boost/thread.hpp>
#include <boost/thread/mutex.hpp>

#include <mining/database.hpp>
#include <network/session/session_manager.hpp>
#include <profile/profile_manager.hpp>


namespace mining
{
    class Brain
    {
    public:
        bool                              alive{ false };
        boost::thread                     threadProcess{};
        network::session::SessionManager* sessionManager{ nullptr };
        mining::Database                  database{};
        profile::ProfileManager           profileManager{};

        void run();

    private:
        static constexpr std::chrono::seconds PROCESS_SESSION_INTERVAL{ 10 };
        static constexpr std::chrono::minutes RELOAD_DATABASE_INTERVAL{ 2 };

        void process();
        bool reloadDatabase();
    };
}
