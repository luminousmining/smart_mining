################################################################################
### CMAKE OPTIONS                                                           ####
################################################################################
cmake_minimum_required(VERSION 3.22)
project(luminousminer VERSION 0.10)

enable_language(C)
enable_language(CXX)

cmake_policy(SET CMP0135 NEW)

################################################################################
### DEFAULT BUILD TYPE                                                      ####
################################################################################
if (NOT CMAKE_BUILD_TYPE)
    message(STATUS "No build type selected, default to Debug")
    set(CMAKE_BUILD_TYPE "Debug" CACHE PATH "Build Type" FORCE)
endif()

################################################################################
### PROJECTS NAME                                                           ####
################################################################################
set(PROXY_EXE proxy)
set(PROXY_UNIT_TEST_EXE proxy_test)

################################################################################
### CXX FLAGS                                                               ####
################################################################################
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_CPPCHECK "cppcheck")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lib)

################################################################################
### CLANG                                                                   ####
################################################################################
set(CMAKE_C_COMPILER "clang-15" CACHE STRING "C compiler" FORCE)
set(CMAKE_CXX_COMPILER "clang++-15" CACHE STRING "C++ compiler" FORCE)
add_compile_options(-W -Wall -Wextra)
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-O0 -g3 -ggdb -v)
else()
    add_compile_options(-O3)
endif()

################################################################################
### BOOST                                                                   ####
################################################################################
set(BOOST_INCLUDEDIR "/usr/local/include/boost")
set(BOOST_LIBRARYDIR "/usr/local/lib")
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(Boost_DEBUG             ON)
    set(Boost_USE_DEBUG_LIBS    ON)
    set(Boost_USE_DEBUG_RUNTIME ON)
    set(Boost_USE_RELEASE_LIBS  OFF)
    set(Boost_DETAILED_FAILURE_MSG ON)
else()
    set(Boost_DEBUG             OFF)
    set(Boost_USE_DEBUG_LIBS    OFF)
    set(Boost_USE_DEBUG_RUNTIME OFF)
    set(Boost_USE_RELEASE_LIBS  ON)
    set(Boost_DETAILED_FAILURE_MSG ON)
endif()
set(Boost_USE_STATIC_LIBS      ON)
set(Boost_USE_MULTITHREADED    ON)
set(Boost_USE_STATIC_RUNTIME   OFF)

################################################################################
### OPENSSL                                                                 ####
################################################################################
set(OPENSSL_USE_STATIC_LIBS TRUE)
set(OPEN_SSL_LIBRARIES OpenSSL::SSL OpenSSL::Crypto)

################################################################################
### FIND PACKAGE | LIBRARIES                                                ####
################################################################################
find_package(Boost 1.86.0 EXACT COMPONENTS atomic chrono filesystem system json thread serialization program_options)
find_package(OpenSSL 1.1.1 REQUIRED COMPONENTS SSL Crypto)
if (UNIX)
    find_package(GnuTLS)
endif()

################################################################################
### HEADERS AND SOURCES FILES PROXY                                         ####
################################################################################
set(PROXY_HEADERS)
set(PROXY_SOURCES
proxy.cpp
)

################################################################################
### HEADERS AND SOURCES FILES PROXY UNIT TEST                               ####
################################################################################
set(PROXY_UNIT_TEST_HEADERS)
set(PROXYUNIT_TEST_SOURCES
proxy_unit_test.cpp
)

################################################################################
## LINK UNIT TEST                                                           ####
################################################################################
# Google Test
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.15.2.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)
enable_testing()
include(GoogleTest)

add_executable(${PROXY_UNIT_TEST_EXE})
#gtest_discover_tests(${PROXY_UNIT_TEST_EXE})

################################################################################
###  LINK MINER                                                             ####
################################################################################
add_executable(${PROXY_EXE})

################################################################################
###  SOURCES                                                                ####
################################################################################
add_subdirectory(algo)
add_subdirectory(common)
add_subdirectory(network)
add_subdirectory(profile)
add_subdirectory(mining)
add_subdirectory(stratum)

set(SOURCES_ALGO ${SOURCES_ALGO})
set(SOURCES_ALGO_TESTS ${SOURCES_ALGO_TESTS})
set(SOURCES_COMMON ${SOURCES_COMMON})
set(SOURCES_COMMON_LOG ${SOURCES_COMMON_LOG})
set(SOURCES_PROFILE ${SOURCES_PROFILE})
set(SOURCES_NETWORK ${SOURCES_NETWORK})
set(SOURCES_NETWORK_SESSION ${SOURCES_NETWORK_SESSION})
set(SOURCES_MINING ${SOURCES_MINING})
set(SOURCES_STRATUM ${SOURCES_STRATUM})


################################################################################
### FILTER SOLUTION VISUAL STUDIO                                            ###
################################################################################
source_group("" FILES proxy.cpp proxy_unit_test.cpp)
source_group("algo" FILES ${SOURCES_ALGO})
source_group("algo/tests" FILES ${SOURCES_ALGO_TESTS})
source_group("common" FILES ${SOURCES_COMMON})
source_group("common/log" FILES ${SOURCES_COMMON_LOG})
source_group("profile" FILES ${SOURCES_PROFILE})
source_group("network" FILES ${SOURCES_NETWORK})
source_group("network/session" FILES ${SOURCES_NETWORK_SESSION})
source_group("mining" FILES ${SOURCES_MINING})
source_group("stratum" FILES ${SOURCES_STRATUM})


################################################################################
###  LINK LIBRARIES                                                         ####
################################################################################
target_link_options(${PROXY_EXE} PUBLIC -static-libstdc++ -static-libgcc)
target_link_options(${PROXY_UNIT_TEST_EXE} PUBLIC -static-libstdc++ -static-libgcc)

target_sources(${PROXY_EXE} PUBLIC
    ${PROXY_HEADERS}
    ${PROXY_SOURCES}
)

target_sources(${PROXY_UNIT_TEST_EXE} PUBLIC
    ${PROXY_UNIT_TEST_HEADERS}
    ${PROXYUNIT_TEST_SOURCES}
)

include_directories(${PROXY_EXE} PUBLIC
    ${Boost_INCLUDE_DIR}
    ${OPENSSL_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

include_directories(${PROXY_UNIT_TEST_EXE} PUBLIC
    ${Boost_INCLUDE_DIR}
    ${OPENSSL_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(${PROXY_EXE}
    ${Boost_LIBRARIES}
    ${OPEN_SSL_LIBRARIES}
)

target_link_libraries(${PROXY_UNIT_TEST_EXE}
    gtest_main
    ${Boost_LIBRARIES}
    ${OPEN_SSL_LIBRARIES}
)

if (UNIX)
    target_link_libraries(${PROXY_EXE}
        ${GNUTLS_LIBRARIES}
        "stdc++fs"
    )
    target_link_libraries(${PROXY_UNIT_TEST_EXE}
        ${GNUTLS_LIBRARIES}
        "stdc++fs"
    )
endif()

################################################################################
### INFORMATIONS                                                            ####
################################################################################
message("=====================================================================")
message("*********************************************************************")
message("-- Platform         : ${CMAKE_SYSTEM_INFO_FILE}")
message("-- Build Type       : ${CMAKE_BUILD_TYPE}")
message("-- Runtime Output   : ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
message("-- Library Output   : ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message("*********************************************************************")
message("-- C COMPILER       : [${CMAKE_C_COMPILER_ID}] ${CMAKE_C_COMPILER}")
message("-- CXX COMPILER     : [${CMAKE_CXX_COMPILER_ID}] ${CMAKE_CXX_COMPILER}")
message("-- CXX Features     : ${CMAKE_CXX_COMPILE_FEATURES}")
message("-- CXX Version      : ${CMAKE_CXX_STANDARD}")
message("-- CXX LINKER FLAGS : ${CMAKE_EXE_LINKER_FLAGS}")
message("-- CXX FLAGS        : ${CMAKE_CXX_FLAGS}")
message("-- CXX FLAGS D      : ${CMAKE_CXX_FLAGS_DEBUG} ")
message("-- CXX FLAGS R      : ${CMAKE_CXX_FLAGS_RELEASE}")
message("*********************************************************************")
message("-- Boost Version    : ${Boost_LIB_VERSION}")
message("-- Boost Include    : ${BOOST_INCLUDEDIR}")
message("-- Boost DirectoryL : ${Boost_LIBRARY_DIRS}")
message("-- Boost Libraries  : ${Boost_LIBRARIES}")
message("*********************************************************************")
message("-- OpenSSL Root Dir : ${OPENSSL_ROOT_DIR}")
message("-- OpenSSL Version  : ${OPENSSL_VERSION}")
message("-- OpenSSL Include  : ${OPENSSL_INCLUDE_DIR}")
message("-- OpenSSL Library  : ${OPEN_SSL_LIBRARIES}")
message("*********************************************************************")
message("*********************************************************************")
message("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LIBRAIRES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
get_target_property(LIST_LIBS ${PROXY_EXE} LINK_LIBRARIES)
string(REPLACE ";" "\n-- " LIST_LIBS "${LIST_LIBS}")
message("-- ${LIST_LIBS}")
message("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
message("=====================================================================")