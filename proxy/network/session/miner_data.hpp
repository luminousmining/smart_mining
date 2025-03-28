#pragma once


#include <mining/miner_table.hpp>
#include <network/stream.hpp>


namespace network
{
    namespace session
    {
        struct MinerData
        {
            bool                logged{ false };
            network::IOStream*  stream{ nullptr };
            mining::MinerTable  table{};

            bool isEmpty() const;
        };
    }
}
