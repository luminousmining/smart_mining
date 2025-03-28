#include <mining/miner_table.hpp>


bool mining::MinerTable::containsCoin(std::string const& tag) const
{
    for (mining::CoinMiner const& coin: listCoin)
    {
        if (coin.coinTag == tag)
        {
            return true;
        }
    }
    return false;
}


mining::CoinMiner mining::MinerTable::getCoinMiner(std::string const& coinTag)
{
    for (auto coin : listCoin)
    {
        if (coin.coinTag == coinTag)
        {
            return coin;
        }
    }
    return {};
}


void mining::MinerTable::addCoinMinable(
    std::string const& coinTag,
    std::string const& algorithm,
    std::string const& hostname,
    uint32_t port,
    std::string const& wallet)
{
    CoinMiner coinConfig
    {
        .coinTag = coinTag,
        .hostname = hostname,
        .port = port,
        .wallet = wallet,
        .algorithm = algorithm
    };
    listCoin.push_back(coinConfig);
}
