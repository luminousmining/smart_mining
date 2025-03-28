#pragma once

#include <chrono>
#include <cstddef>


////////////////////////////////////////////////////////////////////////////////
#define castU2(value) static_cast<unsigned short>(value)
#define castU8(value)  static_cast<uint8_t>(value)
#define castU16(value) static_cast<uint16_t>(value)
#define castU32(value) static_cast<uint32_t>(value)
#define castU64(value) static_cast<uint64_t>(value)

////////////////////////////////////////////////////////////////////////////////
#define cast2(value) static_cast<short>(value)
#define cast8(value)  static_cast<int8_t>(value)
#define cast16(value) static_cast<int16_t>(value)
#define cast32(value) static_cast<int32_t>(value)
#define cast64(value) static_cast<int64_t>(value)

////////////////////////////////////////////////////////////////////////////////
#define castUL(value) static_cast<unsigned long>(value)
#define castLL(value) static_cast<long long>(value)

////////////////////////////////////////////////////////////////////////////////
#define castSize(value)   static_cast<size_t>(value)
#define castDouble(value) static_cast<double>(value)
#define castFloat(value)  static_cast<float>(value)
#define castBool(value)   static_cast<bool>(value)

////////////////////////////////////////////////////////////////////////////////
#define castVOIDP(value)  reinterpret_cast<void*>(value)
#define castVOIDPP(value) reinterpret_cast<void**>(value)
////////////////////////////////////////////////////////////////////////////////
#define castDuration(to, value) std::chrono::duration_cast<to>(value)
#define castNs(value)   castDuration(std::chrono::nanoseconds,  value)
#define castUs(value)   castDuration(std::chrono::microseconds, value)
#define castMs(value)   castDuration(std::chrono::milliseconds, value)
#define castSec(value)  castDuration(std::chrono::seconds,      value)
#define castMin(value)  castDuration(std::chrono::minutes,      value)
#define castHour(value) castDuration(std::chrono::hours,        value)
#define castDay(value)  castDuration(std::chrono::days,         value)
////////////////////////////////////////////////////////////////////////////////