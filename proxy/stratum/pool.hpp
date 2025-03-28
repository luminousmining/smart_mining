#pragma once

#include <string>

#include <boost/json.hpp>


namespace stratum
{
    struct PoolRequest
    {
        int64_t            id{ 0ll };
        std::string        method{};
        boost::json::value params{};

        boost::json::object to_json() const
        {
            boost::json::object obj{};

            obj["id"] = id;
            obj["method"] = method;
            obj["params"] = params;

            return obj;
        }
    };
}
