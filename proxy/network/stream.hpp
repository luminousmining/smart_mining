#pragma once

#include <memory>
#include <string>

#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/json.hpp>
#include <boost/thread/mutex.hpp>


namespace network
{
    struct IOStream
    {
        public:
            boost::mutex                 locker{};
            bool                         ssl{ false };
            boost::asio::streambuf       buffer;
            boost::asio::ssl::context    sslContext{ boost::asio::ssl::context::tlsv12_client };
            boost::asio::ssl::stream<boost::asio::ip::tcp::socket>* socket{ nullptr };

            ~IOStream();

            void initializeContext(boost::asio::io_context& ioContext, bool const isSSL);
            void initializeService(boost::asio::io_service& ioService, bool const isSSL);
            void close();
            bool write(boost::json::value const& request);
            void doSecureConnection();

        private:
            bool onVerifySSL(bool preverified, boost::asio::ssl::verify_context& ctx);
    };

}
