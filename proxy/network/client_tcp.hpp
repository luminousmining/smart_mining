#pragma once

#include <string>
#include <memory>

#include <boost/asio.hpp>
#include <boost/thread.hpp>
#include <boost/json.hpp>

#include <network/stream.hpp>


namespace network
{
    struct ClientTCP
    {
        uint32_t                port{ 0u };
        std::string             hostname{};
        boost::asio::io_service ioService; // TODO: replace by io_context
        boost::thread           threadService{};

        network::IOStream* connect(std::string const& _hostname, uint32_t const _port);
        std::string getAddress() const;
        void run();
        bool handshake(network::IOStream* stream);
    };
}
