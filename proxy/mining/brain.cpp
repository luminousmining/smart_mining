#include <chrono>

#include <boost/chrono.hpp>

#include <common/log/log.hpp>
#include <common/cast.hpp>
#include <mining/brain.hpp>


void mining::Brain::run()
{
    alive = true;

    reloadDatabase();

    threadProcess.interrupt();
    threadProcess = boost::thread{ boost::bind(&mining::Brain::process, this) };
}


void mining::Brain::process()
{
    auto lastProcessSession{ std::chrono::steady_clock::now() };
    auto lastReloadDatabase{ std::chrono::steady_clock::now() };

    logInfo() << "Brain start process!";

    while (true == alive)
    {
        auto const now{ std::chrono::steady_clock::now() };
        auto const elapsedSession{ castSec(now - lastProcessSession) };
        auto const elapsedReloadDatabase{ castMin(now - lastReloadDatabase) };

        if (elapsedSession >= mining::Brain::PROCESS_SESSION_INTERVAL)
        {
            logInfo() << "Process sessions!";
            if (nullptr != sessionManager)
            {
                sessionManager->process();
            }
            lastProcessSession = now;
        }

        if (elapsedReloadDatabase >= mining::Brain::RELOAD_DATABASE_INTERVAL)
        {
            logInfo() << "Reload Database!";
            if (false == reloadDatabase())
            {
                logErr() << "couldn't reload database";
                continue;
            }
            lastReloadDatabase = now;
        }

        boost::this_thread::sleep_for(boost::chrono::milliseconds{ 100 });
    }
}


bool mining::Brain::reloadDatabase()
{
    if (false == database.reload())
    {
        return false;
    }

    if (nullptr != sessionManager)
    {
        if (false == sessionManager->update())
        {
            return false;
        }
    }

    return true;
}
