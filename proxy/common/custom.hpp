#pragma once

#include <boost/thread.hpp>
#include <boost/thread/mutex.hpp>



#define UNIQUE_LOCK(mtxName)\
    boost::unique_lock<boost::mutex> lock{ mtxName };


#define UNIQUE_LOCK_NAME(mtxName, lockName)\
    boost::unique_lock<boost::mutex> lockName{ mtxName };


#define SAFE_DELETE(ptr)\
    {\
        delete ptr;\
        ptr = nullptr;\
    }


#define SAFE_DELETE_ARRAY(ptr)\
    {\
        delete[] ptr;\
        ptr = nullptr;\
    }


#define IS_NULL(function)\
    if (nullptr == (function))\
    {\
        logErr()\
            << "(" << __FUNCTION__ << ":" << __LINE__ << ")"\
            << "(" << #function << ")"\
            << " is nullptr";\
        return false;\
    }


#define NEW(type)\
    new (std::nothrow) type


#define MAX_LIMIT(value, max)\
    (value <= max ? value : max)


#define MIN_LIMIT(value, minimun)\
    (value >= minimun ? value : minimun)


namespace common
{
    template<typename T>
    inline
    void swap(T* a, T* b)
    {
        T const tmp { *a };
        *a = *b;
        *b = tmp;
    }
}
