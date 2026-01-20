#include <functional>

#include <boost/json.hpp>

#include <common/log/log.hpp>
#include <common/boost_utils.hpp>
#include <network/session/session.hpp>


void network::session::Session::receivePacketPool()
{
    if (true == minerData.stream->ssl)
    {
        boost::asio::async_read_until(
            *poolData.stream->socket,
            poolData.stream->buffer,
            '\n',
            std::bind(
                &network::session::Session::onReceivePacketPool,
                this,
                std::placeholders::_1 /*boost::asio::placeholders::error*/,
                std::placeholders::_2 /*boost::asio::placeholders::bytes_transferred*/));
    }
    else
    {
        boost::asio::async_read_until(
            poolData.stream->socket->next_layer(),
            poolData.stream->buffer,
            '\n',
            std::bind(
                &network::session::Session::onReceivePacketPool,
                this,
                std::placeholders::_1 /*boost::asio::placeholders::error*/,
                std::placeholders::_2 /*boost::asio::placeholders::bytes_transferred*/));
    }
}


void network::session::Session::onReceivePacketPool(
     boost::system::error_code const& ec,
     size_t bytes)
{
    try
    {
        if (boost::system::errc::errc_t::success == ec)
        {
            std::string rpc{};
            rpc.assign(boost::asio::buffer_cast<const char*>(poolData.stream->buffer.data()), bytes);
            poolData.stream->buffer.consume(bytes);

            if (   0 < bytes
                && false == rpc.empty())
            {
                executePoolRPC(rpc);
            }
            receivePacketPool();
        }
        else
        {
            if (   boost::asio::error::eof == ec
                || boost::asio::error::connection_aborted == ec
                || boost::asio::error::connection_reset == ec
                || boost::asio::error::connection_refused == ec)
            {
                // TODO: RETRY_CONNECTION
                logMinerInfo() << "disconnected from pool";
                shutdown();
            }
            else
            {
                if (boost::asio::error::operation_aborted != ec)
                {
                    logErr()
                        << "Session pool receive error message"
                        << "[" << ec.value() << "]"
                        << ": " << ec.message();
                    shutdown();
                }
            }
        }
    }
    catch(boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
    }
    catch(std::exception const& e)
    {
        logErr() << e.what();
    }
}


void network::session::Session::executePoolRPC(std::string const& rpc)
{
    auto request{ boost::json::parse(rpc) };
    if (false == request.is_object())
    {
        logErr() << "Parsed request is not an object.";
        return;
    }

    logDebug() << "p<--" << request;

    stratum::PoolStratumCommon rpcPool{};
    const auto& obj{ request.as_object() };

    if (true == common::boostJsonContains(obj, "id"))
    {
        rpcPool.id = common::boostJsonGetNumber<int64_t>(obj.at("id"));
    }

    if (true == common::boostJsonContains(obj, "method"))
    {
        rpcPool.method = common::boostGetString(obj, "method");
    }

    if (true == common::boostJsonContains(obj, "params"))
    {
        rpcPool.params = obj.at("params");
    }

    if (true == common::boostJsonContains(obj, "result"))
    {
        rpcPool.result = obj.at("result");
    }

    if (true == common::boostJsonContains(obj, "error"))
    {
        rpcPool.error = obj.at("error");
    }

    if (false == rpcPool.method.empty())
    {
        stratum::PoolRequest poolRequest
        {
            .id = rpcPool.id,
            .method = rpcPool.method,
            .params = rpcPool.params
        };
        onPoolRequest(poolRequest);
    }
    else
    {
        stratum::Response response
        {
            .id = rpcPool.id,
            .error = rpcPool.error,
            .result = rpcPool.result
        };
        onPoolResponse(response);
    }
}
