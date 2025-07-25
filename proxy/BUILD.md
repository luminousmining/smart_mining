# Requirements
  
## Libraires
- OpenSSL 1.1.1
- boost 1.86.0
  
### Windows
- Visual Studio 2022
- Windows SDK 10.0.22621.0
- CMake >= 3.22.4

### Install
cmake :
https://github.com/Kitware/CMake/releases/tag/v3.22.4 
  
boost :
https://boostorg.jfrog.io/artifactory/main/release/1.86.0/source/boost_1_86_0.zip 
```bat
bootstrap.bat
b2.exe release
b2.exe debug
b2.exe install --prefix=C:\\Boost
```
  
openssl : https://github.com/openssl/openssl.git  
Need Perl :https://github.com/openssl/openssl/blob/master/NOTES-PERL.md 
```bat
git fetch --all
git checkout tags/OpenSSL_1_1_1t
perl Configure VC-WIN64A
```
  
Open `Visual Studio Developer Command Promp x86_x64` with privileges !!!
```bat
nmake
nmake install
```
  
### Linux
- clang++ == 10
- CMake >= 3.22

### Install
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
# Platforms
  
## Windows

```sh
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```
  
## Linux
```sh
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```
