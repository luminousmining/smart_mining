#include <boost/asio.hpp>
#include <boost/exception/diagnostic_information.hpp>

#include <common/log/log.hpp>
#include <common/custom.hpp>
#include <network/server.hpp>
#include <network/stream.hpp>
#include <network/session/session.hpp>


network::ServerTCP::ServerTCP(boost::asio::ip::port_type const _port) :
    port(_port)
{
}


bool network::ServerTCP::bind()
{
    disconnect();

    logInfo() << "Bind server on port " << port;

    try
    {
        using boost_tcp = boost::asio::ip::tcp;
        using boost_endpoint = boost::asio::ip::tcp::endpoint;

        acceptor = boost_tcp::acceptor{ ioContext, boost_endpoint(boost_tcp::v4(), port) };
        acceptor.set_option(boost_tcp::acceptor::reuse_address(true));

        if (false == acceptAsync())
        {
            return false;
        }

        ioContext.run();
    }
    catch(boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
        return false;
    }
    catch (std::exception const& e)
    {
        logErr() << "Bind failed: " << e.what();
        return false;
    }

    return true;
}

bool network::ServerTCP::acceptAsync()
{
    network::IOStream* stream{ NEW(network::IOStream) };
    IS_NULL(stream);

    stream->initializeContext(ioContext, false);

    acceptor.async_accept
    (
        stream->socket->next_layer(),
        boost::bind
        (
            &network::ServerTCP::handlerAccept,
            this,
            stream,
            boost::asio::placeholders::error
        )
    );
    return true;
}


void network::ServerTCP::disconnect()
{
    if (true == acceptor.is_open())
    {
        boost::system::error_code ec;
        acceptor.close(ec);
        if (boost::system::errc::errc_t::success != ec)
        {
            logErr() << "Close listener failed: " << ec.message();
        }
    }
}


void network::ServerTCP::handlerAccept(network::IOStream* stream, boost::system::error_code const& ec)
{
    if (boost::system::errc::errc_t::success != ec)
    {
        logErr() << "Cannot accept client[" << ec.value() << "] " << ec.message();
    }
    else
    {
        logInfo() << "New client";
        sessionManager.createSession(stream);
    }

    if (false == acceptAsync())
    {
        return;
    }
}
