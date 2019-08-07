#pragma once

#include <stdint.h>
#include <cassert>
#include <new>
#include "Alignment.hpp"


template <int ArgSize>
class FunctionWithMaxArgSize
{
public:
    FunctionWithMaxArgSize()
    {
        static_assert (sizeof(NullCallable) == sizeof(storage), "Insufficient storage to create object");
        new (storage)NullCallable();
    }

    template <class T, class ArgType>
    FunctionWithMaxArgSize(void(T::*fn)(ArgType), T* t, ArgType a)
    {
        static_assert(sizeof(ArgType) <= ArgSize, "sizeof(ArgType) is too big. You are trying to instantiate a Function object with an argument that exceeds the maximum size.");
        static_assert (sizeof(CallableWithArg<T, ArgType>) == sizeof(storage), "Insufficient storage to create object");
        new (storage)CallableWithArg<T, ArgType>(fn, t, a);
    }

    template <class T>
    FunctionWithMaxArgSize(void(T::*fn)(), T* t)
    {
        static_assert (sizeof(CallableNoArg<T>) == sizeof(storage), "Insufficient storage to create object");
        new (storage)CallableNoArg<T>(fn, t);
    }

    void operator()() const
    {
        (*reinterpret_cast<const Callable*>(storage))();
    }

private:
    class Callable
    {
    public:
        virtual ~Callable() {}
        virtual void operator()() const = 0;

    protected:
        char functionStorage[sizeof(void(Callable::*)())];
        char instanceStorage[sizeof(void*)];
        char argumentStorage[ArgSize];
    };

    template <class T, class ArgType>
    class CallableWithArg : public Callable
    {
    public:
        CallableWithArg(void(T::*fn)(ArgType), T* t, ArgType a)
        {
            static_assert(sizeof(Callable::functionStorage) == sizeof(void(T::*)()), "Function storage is too small to hold the pointer to member function");
            static_assert(sizeof(Callable::instanceStorage) == sizeof(T*), "Instance storage is too small to hold the instance pointer");
            static_assert(sizeof(Callable::argumentStorage) >= sizeof(ArgType), "Argument storage is too small to hold the argument");

            memcpy(Callable::functionStorage, &fn, sizeof(void(T::*)()));
            memcpy(Callable::instanceStorage, &t, sizeof(T*));
            memcpy(Callable::argumentStorage, &a, sizeof(ArgType));
        }

        void operator()() const override
        {
            void(T::*fn)(ArgType);
            T* t;
            ArgType a;

            memcpy(&fn, Callable::functionStorage, sizeof(void(T::*)()));
            memcpy(&t, Callable::instanceStorage, sizeof(T*));
            memcpy(&a, Callable::argumentStorage, sizeof(ArgType));

            (t->*fn)(a);
        }
    };

    template <class T>
    class CallableNoArg : public Callable
    {
    public:
      CallableNoArg(void(T::*fn)(), T* t)
      {
          static_assert(sizeof(Callable::functionStorage) == sizeof(void(T::*)()), "Function storage is too small to hold the pointer to member function");
          static_assert(sizeof(Callable::instanceStorage) == sizeof(T*), "Instance storage is too small to hold the instance pointer");

          memcpy(Callable::functionStorage, &fn, sizeof(void(T::*)()));
          memcpy(Callable::instanceStorage, &t, sizeof(T*));
      }

      void operator()() const override
      {
          void(T::*fn)();
          T* t;

          memcpy(&fn, Callable::functionStorage, sizeof(void(T::*)()));
          memcpy(&t, Callable::instanceStorage, sizeof(T*));

          (t->*fn)();
      }
    };

    struct NullCallable : public Callable
    {
        void operator()() const override {}
    };

    alignas(alignof(Callable)) char storage[sizeof(Callable)];
};

class Function : public FunctionWithMaxArgSize<MaxSizeForTypes<int32_t, bool, float, const char*>::value>
{
public:
  Function()
    : FunctionWithMaxArgSize()
  {}

  template <class T, class ArgType>
  Function(void(T::*fn)(ArgType), T* t, ArgType a)
    : FunctionWithMaxArgSize(fn, t, a)
  {}

  template <class T>
  Function(void(T::*fn)(), T* t)
    : FunctionWithMaxArgSize(fn, t)
  {}
};
