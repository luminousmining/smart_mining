#include <functional>

#include <boost/exception/diagnostic_information.hpp>

#include <common/log/log.hpp>
#include <common/boost_utils.hpp>
#include <network/session/session.hpp>


void network::session::Session::receivePacketMiner()
{
    if (true == minerData.stream->ssl)
    {
        boost::asio::async_read_until(
            *minerData.stream->socket,
            minerData.stream->buffer,
            '\n',
            std::bind(
                &network::session::Session::onReceivePacketMiner,
                this,
                std::placeholders::_1  /*boost::asio::placeholders::error*/,
                std::placeholders::_2 /*boost::asio::placeholders::bytes_transferred*/));
    }
    else
    {
        boost::asio::async_read_until(
            minerData.stream->socket->next_layer(),
            minerData.stream->buffer,
            '\n',
            std::bind(
                &network::session::Session::onReceivePacketMiner,
                this,
                std::placeholders::_1 /*boost::asio::placeholders::error*/,
                std::placeholders::_2 /*boost::asio::placeholders::bytes_transferred*/));
    }
}


void network::session::Session::onReceivePacketMiner(
     boost::system::error_code const& ec,
    size_t bytes)
{
    try
    {
        if (boost::system::errc::errc_t::success == ec)
        {
            std::string rpc{};
            rpc.assign(boost::asio::buffer_cast<const char*>(minerData.stream->buffer.data()), bytes);
            minerData.stream->buffer.consume(bytes);

            if (false == rpc.empty())
            {
                executeMinerRPC(rpc);
            }

            receivePacketMiner();
        }
        else
        {
            if (boost::asio::error::operation_aborted != ec)
            {
                shutdown();
            }
        }
    }
    catch(boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
        shutdown();
    }
    catch(std::exception const& e)
    {
        logErr() << e.what();
        shutdown();
    }
}


void network::session::Session::executeMinerRPC(std::string const& rpc)
{
    auto const request{ boost::json::parse(rpc) };
    if (false == request.is_object())
    {
        logErr() << "Parsed request is not an object.";
        return;
    }

    logDebug() << "m<--" << request;

    stratum::MinerRequest rpcRequest{};
    const auto& obj{ request.as_object() };
    if (true == common::boostJsonContains(obj, "id"))
    {
        rpcRequest.id =  common::boostJsonGetNumber<int64_t>(obj.at("id"));
    }

    if (true == common::boostJsonContains(obj, "method"))
    {
        rpcRequest.method = common::boostGetString(obj, "method");
    }

    if (true == common::boostJsonContains(obj, "params"))
    {
        rpcRequest.params = obj.at("params");
    }

    onMethodMiner(rpcRequest);
}
