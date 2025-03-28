#pragma once

#include <string>

#include <network/client_tcp.hpp>


namespace network
{
    namespace session
    {
        struct PoolData
        {
            network::ClientTCP client{};
            network::IOStream* stream{ nullptr };
            std::string        fullname{};
            std::string        extranonce{};
            uint32_t           extranonce2{ 0u };

            void clean();
        };
    }
}
