#pragma once

#include <profile/data_base.hpp>


namespace profile
{
    struct ProfileDataMarketcap : public ProfileDataBase
    {
        double marketCap{ 0.0 };
    };
}
