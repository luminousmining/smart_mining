#include <common/boost_utils.hpp>


bool common::boostJsonContains(
    boost::json::object const& obj,
    std::string const& keyName)
{
    return obj.find(keyName) != obj.end();
}


std::string common::boostGetString(
    boost::json::object const& obj,
    std::string const& keyName)
{
    using namespace std::string_literals;

    if (false == common::boostJsonContains(obj, keyName))
    {
        logErr() << "object[" << obj << "] doest not contains key[" << keyName << "]";
        return ""s;
    }

    try
    {
        return std::string(obj.at(keyName).as_string().c_str());
    }
    catch(boost::system::system_error const& e)
    {
        logErr()
            << "[" << e.code() << "]" << "["<< e.what() << "]"
            << "object[" << obj << "] can not get string on key [" << keyName << "]";
    }
    catch (boost::exception const& e)
    {
        logErr()
            << "object[" << obj << "] can not get string on key [" << keyName << "]"
            << diagnostic_information(e);
    }

    return ""s;
}


std::string common::boostGetString(
    boost::json::array const& obj,
    uint32_t const index)
{
    using namespace std::string_literals;

    try
    {
        auto it{ obj.at(index) };
        if (true == it.is_null())
        {
            return ""s;
        }
        if (false == it.is_string())
        {
            return ""s;
        }
        return std::string(it.as_string().c_str());
    }
    catch(boost::system::system_error const& e)
    {
        logErr()
            << "[" << e.code() << "]" << "["<< e.what() << "]"
            << "object[" << obj << "] can not get string on index [" << index << "]";
    }
    catch (boost::exception const& e)
    {
        logErr()
            << "object[" << obj << "] can not get string on index [" << index << "]"
            << diagnostic_information(e);
    }

    return ""s;
}
