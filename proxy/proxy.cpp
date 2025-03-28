#include <thread>

#include <boost/asio.hpp>

#include <network/server.hpp>
#include <common/log/log.hpp>
#include <mining/database.hpp>
#include <mining/brain.hpp>


int main()
{
    logInfo() << "Start proxy";

    network::ServerTCP  proxy{ 7878 };
    mining::Brain brain{};

    setLogLevel(common::TYPELOG::__DEBUG);

    proxy.sessionManager.process();

    brain.sessionManager = &proxy.sessionManager;
    brain.sessionManager->database = &brain.database;
    brain.sessionManager->profileManager = &brain.profileManager;
    brain.run();

    logInfo() << "Attempting to bind proxy server...";
    if (false == proxy.bind())
    {
        logErr() << "Failed to bind proxy server";
        return 1;
    }
    logInfo() << "Successfully bound proxy server, starting to listen...";

    return 0;
}
