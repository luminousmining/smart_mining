#include <network/session/pool_data.hpp>


void network::session::PoolData::clean()
{
    fullname.clear();
    extranonce.clear();
    extranonce2 = 0u;
}
