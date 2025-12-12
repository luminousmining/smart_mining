# Installation Guide for Linux
  
## Dependencies
- CMake >= 3.22.4
- OpenSSL == 1.1.1
- boost == 1.86.0
  
## Install
cmake: https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.sh  
  
compiler :
```bah
sudo apt install -y build-essential libstdc++-10-dev gnutls-dev cppcheck checkinstall clang-10 libx11-dev
```
  
openssl :
```sh
git clone https://github.com/openssl/openssl.git
cd openssl
./Configure
make
sudo make install
```
  
boost : 
```sh
wget --no-check-certificate https://archives.boost.io/release/1.86.0/source/boost_1_86_0.tar.gz
tar -xvf boost_1_86_0.tar.gz
cd boost_1_86_0
./bootstrap.sh --prefix=/usr/local
./b2 debug release
sudo ./b2 install
```

## Build
```sh
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```
