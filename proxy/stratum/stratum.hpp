#pragma once


namespace stratum
{
    // Stratum IDs
    constexpr int64_t STRATUM_ID_NOTIFY = 0;
    constexpr int64_t STRATUM_ID_SUBSCRIBE = 1;
    constexpr int64_t STRATUM_ID_AUTHORIZE = 2;
    constexpr int64_t STRATUM_ID_SUBMIT_MINIMAL = 3;

    // Mining Methods
    inline constexpr const char* STRATUM_METHOD_MINING_SUBSCRIBE = "mining.subscribe";
    inline constexpr const char* STRATUM_METHOD_MINING_SUBMIT = "mining.submit";
    inline constexpr const char* STRATUM_METHOD_MINING_NOTIFY = "mining.notify";

    // Smart Mining IDs
    constexpr int64_t SM_ID_SET_ALGO = 1;
    constexpr int64_t SM_ID_SET_EXTRA_NONCE = 2;

    // Smart Mining Methods
    inline constexpr const char* STRATUM_METHOD_SM_SET_EXTRA_NONCE = "smart_mining.set_extra_nonce";
    inline constexpr const char* STRATUM_METHOD_SM_SET_ALGO = "smart_mining.set_algo";
    inline constexpr const char* STRATUM_METHOD_SM_SET_PROFILE = "smart_mining.set_profile";

    struct Response
    {
    public:
        int64_t            id{ 0ll };
        boost::json::value error{};
        boost::json::value result{};

        boost::json::object to_json() const
        {
            boost::json::object obj;

            obj["id"] = id;

            if (false == error.is_null())
            {
                obj["error"] = error;
            }

            if (false == result.is_null())
            {
                obj["result"] = result;
            }

            return obj;
        }
    };

    struct PoolStratumCommon
    {
        int64_t            id{ 0ll };
        std::string        method{};
        boost::json::value params{};
        boost::json::value result{};
        boost::json::value error{};

        boost::json::object to_json() const
        {
            boost::json::object obj;
            
            // Only include fields that are set
            if (id != 0)
            {
                obj["id"] = id;
            }
            if (false == method.empty())
            {
                obj["method"] = method;
            }
            if (false == params.is_null())
            {
                obj["params"] = params;
            }
            if (false == result.is_null())
            {
                obj["result"] = result;
            }
            if (false == error.is_null())
            {
                obj["error"] = error;
            }
            
            return obj;
        }
    };

}