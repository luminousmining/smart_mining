#pragma once

#include <profile/data_base.hpp>


namespace profile
{
    struct ProfileDataEmission : public ProfileDataBase
    {
        double emissionUsd{ 0.0 };
    };
}
