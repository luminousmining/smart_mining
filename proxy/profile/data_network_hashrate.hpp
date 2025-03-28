#pragma once

#include <profile/data_base.hpp>


namespace profile
{
    struct ProfileDataNetworkHashrate : public ProfileDataBase
    {
        double networkHashrate{ 0.0 };
    };
}
