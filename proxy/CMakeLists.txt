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
set(SOURCES_ALGO)
set(SOURCES_ALGO_TESTS)
set(SOURCES_COMMON)
set(SOURCES_COMMON_LOG)
set(SOURCES_PROFILE)
set(SOURCES_NETWORK)
set(SOURCES_NETWORK_SESSION)
set(SOURCES_MINING)
set(SOURCES_STRATUM)


add_subdirectory(algo)
add_subdirectory(common)
add_subdirectory(network)
add_subdirectory(profile)
add_subdirectory(mining)
add_subdirectory(stratum)

set(SOURCES_ALGO ${SOURCES_ALGO} PARENT_SCOPE)
set(SOURCES_ALGO_TESTS ${SOURCES_ALGO_TESTS} PARENT_SCOPE)
set(SOURCES_COMMON ${SOURCES_COMMON} PARENT_SCOPE)
set(SOURCES_COMMON_LOG ${SOURCES_COMMON_LOG} PARENT_SCOPE)
set(SOURCES_PROFILE ${SOURCES_PROFILE} PARENT_SCOPE)
set(SOURCES_NETWORK ${SOURCES_NETWORK} PARENT_SCOPE)
set(SOURCES_NETWORK_SESSION ${SOURCES_NETWORK_SESSION} PARENT_SCOPE)
set(SOURCES_MINING ${SOURCES_MINING} PARENT_SCOPE)
set(SOURCES_STRATUM ${SOURCES_STRATUM} PARENT_SCOPE)


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
if (NOT WIN32)
    target_link_options(${PROXY_EXE} PUBLIC -static-libstdc++ -static-libgcc)
    target_link_options(${PROXY_UNIT_TEST_EXE} PUBLIC -static-libstdc++ -static-libgcc)
endif()

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
