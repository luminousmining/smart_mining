#include <common/log/log.hpp>
#include <common/custom.hpp>
#include <network/session/session_manager.hpp>
#include <network/session/session.hpp>


bool network::session::SessionManager::createSession(
        network::IOStream* stream)
{
    UNIQUE_LOCK(locker);

    network::session::Session* session{ NEW(network::session::Session) };
    IS_NULL(session);

    session->alive = true;
    session->minerData.stream = stream;
    session->database = database;
    session->profileManager = profileManager;

    session->receivePacketMiner();

    sessions.push_back(session);

    return true;
}


size_t network::session::SessionManager::getSessionCount() const
{
    return sessions.size();
}


void network::session::SessionManager::process()
{
    UNIQUE_LOCK(locker);

    size_t const sessionAliveBeforeCount{ getSessionCount() };
    sessions.erase
    (
        std::remove_if
        (
            sessions.begin(),
            sessions.end(),
            [](network::session::Session* session)
            {
                return nullptr == session || false == session->isAlive();
            }
        ),
        sessions.end()
    );

    size_t const sessionAliveCount{ getSessionCount() };
    if (sessionAliveBeforeCount != sessionAliveCount)
    {
        size_t const deletedCount{ sessionAliveBeforeCount - sessionAliveCount };
        logInfo() << "Deleted [" << deletedCount << "] sessions!";
    }

    logInfo() << "[" << sessionAliveCount << "] sessions alive";
}


bool network::session::SessionManager::update()
{
    UNIQUE_LOCK(locker);

    for (auto session : sessions)
    {
        if (   nullptr != session
            || false == session->alive)
        {
            continue;
        }

        // Duplicate line !
        // En fonction du profile de la session
        std::string const coinName{ profileManager->findBestCoin(session->minerData.table, database->profileUsdSec) };

        if (coinName != session->currentCoin.coinTag)
        {
            session->switchCoin(coinName);
        }
    }

    return true;
}
