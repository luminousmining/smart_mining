#pragma once


#include <boost/exception/diagnostic_information.hpp>
#include <boost/json.hpp>

#include <common/cast.hpp>
#include <common/log/log.hpp>


namespace common
{
    template<typename T>
    inline
    T boostJsonGetNumber(boost::json::value const& v)
    {
        try
        {
            if (true == v.is_null())
            {
                return static_cast<T>(0);
            }
            if (true == v.is_double())
            {
                return static_cast<T>(v.as_double());
            }
            else if (true == v.is_uint64())
            {
                return static_cast<T>(v.as_uint64());
            }
            else if(true == v.is_string())
            {
                std::string str{ v.as_string().c_str() };
                if (true == str.empty())
                {
                    return T{ 0 };
                }
                return std::stod(str);
            }
        }
        catch (boost::system::system_error const& e)
        {
            logErr() << "[" << e.code() << "]" << "["<< e.what() << "]";
            return T{0};
        }
        catch(boost::exception const& e)
        {
            logErr() << diagnostic_information(e);
            return T{0};
        }

        return static_cast<T>(v.as_int64());
    }

    bool boostJsonContains(boost::json::object const& obj,
                           std::string const& keyName);
    std::string boostGetString(boost::json::object const& obj,
                               std::string const& keyName);
    std::string boostGetString(boost::json::array const& obj,
                               uint32_t const index);
}
