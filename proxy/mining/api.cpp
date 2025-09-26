#include <string>

#include <boost/exception/diagnostic_information.hpp>
#include <boost/beast.hpp>
#include <boost/asio.hpp>
#include <boost/json.hpp>

#include <common/log/log.hpp>
#include <mining/api.hpp>


boost::json::value mining::apiGet(std::string const& endpoint)
{
    namespace http = boost::beast::http;
    namespace asio = boost::asio;
    namespace json = boost::json;

    asio::io_context        ioc{};
    json::value             json_response{};
    asio::ip::tcp::resolver resolver{ioc};
    asio::ip::tcp::socket   socket{ioc};

    try
    {

        // Resolve connection
        auto const results{ resolver.resolve(mining::API_HOST, mining::API_PORT) };
        asio::connect(socket, results.begin(), results.end());

        // Set request
        std::string target{ endpoint + "?api_key=" + mining::API_KEY };
        http::request<http::string_body> req
        {
            http::verb::get,
            target,
            mining::API_VERSION_HTTP
        };
        req.set(http::field::host, API_HOST);
        req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);

        // Send
        logDebug() << "GET: " << target;
        http::write(socket, req);

        // Read
        boost::beast::flat_buffer         buffer{};
        http::response<http::string_body> res{};
        http::read(socket, buffer, res);

        // Close socket
        socket.shutdown(asio::ip::tcp::socket::shutdown_both);

        // Parse response
        json_response = json::parse(res.body());
    }
    catch(boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
        return json::value();
    }

    return json_response;
}


boost::json::array mining::apiInfoCoins()
{
    return apiGet("/info/coins").as_array();
}


boost::json::object mining::apiInfoCoin(std::string const& tag)
{
    std::string endpoint{ "/info/coin/" + tag };
    return apiGet(endpoint).as_object();
}


boost::json::array mining::apiProfileEmission()
{
    return apiGet("/profile/emission").as_array();
}


boost::json::array mining::apiProfileHashUsd()
{
    return apiGet("/profile/hash_usd").as_array();
}


boost::json::array mining::apiProfileUsdSec()
{
    return apiGet("/profile/usd_sec").as_array();
}


boost::json::array mining::apiProfileMarketCap()
{
    return apiGet("/profile/market_cap").as_array();
}


boost::json::array mining::apiProfileNetworkHashrate(bool const greater)
{
    if (true == greater)
    {
        return apiGet("/profile/network_hashrate/greater").as_array();
    }
    return apiGet("/profile/network_hashrate/less").as_array();
}
