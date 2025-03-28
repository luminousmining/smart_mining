#include <boost/asio.hpp>
#include <boost/exception/diagnostic_information.hpp>

#include <common/log/log.hpp>
#include <common/custom.hpp>
#include <network/client_tcp.hpp>


std::string network::ClientTCP::getAddress() const
{
    return hostname + ":" + std::to_string(port);
}


void network::ClientTCP::run()
{
    threadService.interrupt();
    threadService = boost::thread{ boost::bind(&boost::asio::io_service::run, &ioService) };
}


network::IOStream* network::ClientTCP::connect(std::string const& _hostname, uint32_t const _port)
{
    network::IOStream* stream{ NEW(network::IOStream) };
    if (nullptr == stream)
    {
        return nullptr;
    }
    stream->initializeService(ioService, false);

    hostname = _hostname;
    port = _port;

    try
    {
        boost::system::error_code ec{};
        auto const address{ boost::asio::ip::address::from_string(hostname, ec) };

        if (boost::system::errc::errc_t::success != ec)
        {
            boost::asio::ip::tcp::resolver        resolver{ ioService };
            boost::asio::ip::tcp::resolver::query query{ hostname, std::to_string(port) };
            auto                                  endpoints{ resolver.resolve(query, ec) };

            if (boost::system::errc::errc_t::success != ec)
            {
                logErr() << "Cannot resolve " << hostname << ":" << port;
                if (nullptr != stream)
                {
                    SAFE_DELETE(stream);
                }
                return nullptr;
            }

            boost::asio::connect(stream->socket->next_layer(), endpoints, ec);
            if (boost::system::errc::errc_t::success != ec)
            {
                logErr() << "Cannot connect to DNS " << hostname << ":" << port;
                if (nullptr != stream)
                {
                    SAFE_DELETE(stream);
                }
                return nullptr;
            }
        }
        else
        {
            boost::asio::ip::tcp::endpoint endpoint{ address, static_cast<boost::asio::ip::port_type>(port) };
            stream->socket->next_layer().connect(endpoint, ec);
            if (boost::system::errc::errc_t::success != ec)
            {
                logErr() << "Cannot connect to host " << hostname << ":" << port;
                if (nullptr != stream)
                {
                    SAFE_DELETE(stream);
                }
                return nullptr;
            }
        }

        stream->socket->next_layer().set_option(boost::asio::socket_base::keep_alive(true));
        stream->socket->next_layer().set_option(boost::asio::ip::tcp::no_delay(true));

        if (true == stream->ssl)
        {
            if (false == handshake(stream))
            {
                if (nullptr != stream)
                {
                    SAFE_DELETE(stream);
                }
                return nullptr;
            }
        }
    }
    catch(boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
        if (nullptr != stream)
        {
            SAFE_DELETE(stream);
        }
    }
    catch (std::exception const& e)
    {
        logErr() << e.what();
        if (nullptr != stream)
        {
            SAFE_DELETE(stream);
        }
    }

    return stream;
}


bool network::ClientTCP::handshake(network::IOStream* stream)
{
    boost::system::error_code ec{};

    stream->socket->handshake(boost::asio::ssl::stream_base::client, ec);

    if (boost::system::errc::errc_t::success != ec)
    {
        logErr() << "Cannot connect to pool with SSL option";
        if (337047686 == ec.value())
        {
            logErr()
                << "\n"
                << "This can have multiple reasons:" << "\n"
                << "* Root certs are either not installed or not found" << "\n"
                << "* Pool uses a self-signed certificate" << "\n"
                << "* Pool hostname you're connecting to does not match"
                << " the CN registered for the certificate." << "\n"
#if !defined(_WIN32)
                << "Possible fixes:" << "\n"
                << "* Make sure the file '/etc/ssl/certs/ca-certificates.crt' exists and"
                << " is accessible" << "\n"
                << "* Export the correct path via 'export " << "\n"
                << "SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt' to the correct"
                << " file" << "\n"
                << " On most systems you can install"
                << " the 'ca-certificates' package" << "\n"
                << " You can also get the latest file here: " << "\n"
                << "https://curl.haxx.se/docs/caextract.html" << "\n"
#endif
                ;
        }
        return false;
    }

    return true;
}
