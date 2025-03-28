#include <boost/thread.hpp>
#include <boost/chrono.hpp>

#include <common/log/log.hpp>
#include <common/custom.hpp>
#include <network/session/session.hpp>


bool network::session::Session::connectToPool()
{
    poolData.fullname = currentCoin.hostname + ":" + std::to_string(currentCoin.port);
    poolData.stream =  poolData.client.connect(currentCoin.hostname , currentCoin.port);

    if (nullptr == poolData.stream)
    {
        return false;
    }

    if (false == sendPoolSubscribe())
    {
        return false;
    }

    receivePacketPool();

    poolData.client.run();

    return true;
}


void network::session::Session::closeStreamMiner()
{
    UNIQUE_LOCK(minerData.stream->locker);
    if (nullptr != minerData.stream)
    {
        minerData.stream->close();
    }
}


void network::session::Session::closeStreamPool()
{
    minerData.logged = false;

    if (nullptr != poolData.stream)
    {
        UNIQUE_LOCK(poolData.stream->locker);
        poolData.stream->close();
    }
    poolData.client.threadService.interrupt();
    poolData.clean();
}


void network::session::Session::shutdown()
{
    logInfo() << "Disconnecting miner from pool " << poolData.fullname;

    closeStreamPool();
    closeStreamMiner();

    alive = false;
}


bool network::session::Session::sendToMiner(boost::json::value const& request)
{
    UNIQUE_LOCK(minerData.stream->locker);
    if (nullptr == minerData.stream)
    {
        return false;
    }
    logDebug() << "m-->" << request;
    return minerData.stream->write(request);
}


bool network::session::Session::sendToPool(boost::json::value const& request)
{
    UNIQUE_LOCK(poolData.stream->locker);
    if (nullptr == poolData.stream)
    {
        return false;
    }
    logDebug() << "p-->" << request;
    return poolData.stream->write(request);
}


bool network::session::Session::isAlive() const
{
    return alive;
}


bool network::session::Session::isLogged(std::string const& functionName) const
{
    if (false == minerData.logged)
    {
        logMinerErr() << "[" << functionName << "] => Miner was not logged!";
        return false;
    }

    return true;
}


bool network::session::Session::switchCoin(std::string const& coinTag)
{
    currentCoin = minerData.table.getCoinMiner(coinTag);

    logMinerInfo() << "switch for coin[" << coinTag << "]";

    closeStreamPool();
    boost::this_thread::sleep_for(boost::chrono::seconds{ 1 });

    return connectToPool();
}
