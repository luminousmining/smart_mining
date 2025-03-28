#pragma once

#include <string>
#include <memory>

#include <boost/asio.hpp>
#include <boost/thread.hpp>

#include <network/session/session_manager.hpp>


namespace network
{
    class ServerTCP
    {
    public:
        boost::asio::ip::port_type       port{};
        boost::asio::io_context          ioContext{};
        boost::asio::ip::tcp::acceptor   acceptor{ ioContext };
        network::session::SessionManager sessionManager;

        ServerTCP(boost::asio::ip::port_type const _port);
        ~ServerTCP() = default;

        bool bind();
        bool acceptAsync();
        void disconnect();

    private:
        void handlerAccept(network::IOStream* stream, boost::system::error_code const& error);
    };

}