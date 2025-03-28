#include <boost/exception/diagnostic_information.hpp>

#include <network/session/session.hpp>


bool network::session::Session::sendSmartMiningSetAlgorithm()
{
    using namespace std::string_literals;

    stratum::ProxyRequest request
    {
        .id = stratum::SM_ID_SET_ALGO,
        .method = stratum::STRATUM_METHOD_SM_SET_ALGO,
        .params = boost::json::value(currentCoin.algorithm)
    };

    return sendToMiner(request.to_json());
}


bool network::session::Session::sendSmartMiningSetExtranonce(std::string const& extraNonce)
{
    stratum::MinerRequest response
    {
        .id = stratum::SM_ID_SET_EXTRA_NONCE,
        .method = stratum::STRATUM_METHOD_SM_SET_EXTRA_NONCE,
        .params = boost::json::value(extraNonce)
    };

    return sendToMiner(response.to_json());
}


bool network::session::Session::sendSmartMiningSetExtranonce2(
    std::string const& extraNonce,
    int32_t const extranonceSize)
{
    boost::json::array params
    {
        boost::json::value(extraNonce),
        boost::json::value(extranonceSize)
    };

    stratum::MinerRequest response
    {
        .id = stratum::SM_ID_SET_EXTRA_NONCE,
        .method = stratum::STRATUM_METHOD_SM_SET_EXTRA_NONCE,
        .params = params
    };

    return sendToMiner(response.to_json());
}
