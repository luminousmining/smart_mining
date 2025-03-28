#if defined(_WIN32)
#pragma comment(lib, "crypt32.lib")
#endif

#include <cstdlib>
#include <sstream>

#include <boost/asio.hpp>
#include <boost/exception/diagnostic_information.hpp>
#include <boost/system/error_code.hpp>

#include <common/log/log.hpp>
#include <common/custom.hpp>
#include <network/stream.hpp>

#if defined(_WIN32)
#include <wincrypt.h>
#endif


network::IOStream::~IOStream()
{
    if (nullptr != socket)
    {
        close();
    }
    SAFE_DELETE(socket);
}


void network::IOStream::initializeContext(boost::asio::io_context& ioContext, bool const isSSL)
{
    ssl = isSSL;
    if (true == ssl)
    {
         doSecureConnection();
    }
    else
    {
        sslContext.set_verify_mode(boost::asio::ssl::verify_none);
    }
    socket = NEW(boost::asio::ssl::stream<boost::asio::ip::tcp::socket>(ioContext, sslContext));
}


void network::IOStream::initializeService(boost::asio::io_service& ioService, bool const isSSL)
{
    ssl = isSSL;
    if (true == ssl)
    {
         doSecureConnection();
    }
    else
    {
        sslContext.set_verify_mode(boost::asio::ssl::verify_none);
    }
    socket = NEW(boost::asio::ssl::stream<boost::asio::ip::tcp::socket>(ioService, sslContext));
}



void network::IOStream::close()
{
    boost::system::error_code ec{};

    if (nullptr == socket)
    {
        return;
    }

    if (socket->next_layer().is_open())
    {
        socket->next_layer().shutdown(boost::asio::ip::tcp::socket::shutdown_both, ec);
        socket->next_layer().close(ec);
    }
    else
    {
        socket->next_layer().cancel();
    }

    logDebug() << "Stream closed!";
}


bool network::IOStream::write(const boost::json::value& request)
{
    if (false == socket->next_layer().is_open())
    {
        return false;
    }

    try
    {
        std::string jsonString{ boost::json::serialize(request) };
        jsonString += "\n";

        boost::system::error_code ec;
        boost::asio::write(socket->next_layer(), boost::asio::buffer(jsonString), ec);

        if (boost::system::errc::errc_t::success != ec)
        {
            logErr() << "Write error: " << ec.message();
            return false;
        }
    }
    catch(boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
        return false;
    }
    catch (std::exception const& e)
    {
        logErr() << "Write exception: " << e.what();
        return false;
    }

    return true;
}


bool network::IOStream::onVerifySSL(
    [[maybe_unused]] bool preverified,
    boost::asio::ssl::verify_context& ctx)
{
    auto const* cert{ X509_STORE_CTX_get_current_cert(ctx.native_handle()) };
    if (nullptr == cert)
    {
        logErr() << "Certificat is incorrect.";
        return false;
    }

    return true;
}

void network::IOStream::doSecureConnection()
{
    try
    {
        sslContext.set_verify_mode(boost::asio::ssl::verify_peer);
        sslContext.set_verify_callback(
            boost::bind(
                &network::IOStream::onVerifySSL,
                this,
                std::placeholders::_1,
                std::placeholders::_2));

#if defined(_WIN32)
        auto certStore{ CertOpenSystemStore(0, "ROOT") };
        if (nullptr == certStore)
        {
            logErr() << "Certifcat Store \"ROOT\" was not found !";
            return false;
        }

        auto* store{ X509_STORE_new() };
        PCCERT_CONTEXT certContext{ nullptr };
        while (nullptr != (certContext = CertEnumCertificatesInStore(certStore, certContext)))
        {
            auto* x509
            {
                d2i_X509
                (
                    nullptr,
                    const_cast<const unsigned char**>(&(certContext->pbCertEncoded)),
                    certContext->cbCertEncoded
                )
            };
            if (nullptr != x509)
            {
                X509_STORE_add_cert(store, x509);
                X509_free(x509);
            }
        }

        CertFreeCertificateContext(certContext);
        CertCloseStore(certStore, 0);
        SSL_CTX_set_cert_store(sslContext.native_handle(), store);
#elif defined(__linux__)
        try
        {
            char* certPath{ std::getenv("SSL_CERT_FILE") };
            sslContext.load_verify_file
            (
                nullptr != certPath
                    ? certPath
                    : "/etc/ssl/certs/ca-certificates.crt"
            );
        }
        catch (...)
        {
            logErr()
                << "Failed to load ca certificates. Either the file"
                << " '/etc/ssl/certs/ca-certificates.crt' does not exist" << "\n"
                << "or the environment variable SSL_CERT_FILE is set to an invalid or"
                << " inaccessible file." << "\n"
                << "It is possible that certificate verification can fail.";
        }
#endif
    }
    catch (boost::exception const& e)
    {
        logErr() << diagnostic_information(e);
    }
    catch (std::exception const& e)
    {
        logErr() << e.what();
    }
}
