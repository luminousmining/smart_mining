#pragma once

#include <string>


namespace mining
{
    struct CoinMiner
    {
        std::string coinTag{};
        std::string hostname{};
        uint32_t    port{ 0u };
        std::string wallet{};
        std::string algorithm{};
    };
}
