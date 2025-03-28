#pragma once


namespace mining
{
    struct CoinTable
    {
        std::string name{};
        std::string tag{};
        std::string algorithm{};
        double usd{ 0.f };
        double usdSec{ 0.f };
        double difficulty{ 0.f };
        double networkHashrate{ 0.f };
        double emissionCoin{ 0.f };
        double emissionUsd{ 0.f };
    };
}
