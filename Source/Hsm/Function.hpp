#pragma once

#include <stdint.h>
#include <cassert>
#include  <new>

class Function
{
public:
    Function()
    {
        new (storage) NullCallable();
    }

    template <class T>
    Function(void(T::*fn)(), T* t)
    {
        new (storage)Callable<T>(fn, t);
    }

    void operator()() const
    {
        (*reinterpret_cast<const CallableBase*>(storage))();
    }

private:
    class CallableBase
    {
    public:
	    virtual ~CallableBase() {}
	    virtual void operator()() const = 0;

    protected:
        uint8_t functionStorage[sizeof(void*)];
        uint8_t instanceStorage[sizeof(void*)];
    };

    template <class T>
    class Callable : public CallableBase
    {
    public:
        Callable(void(T::*fn)(), T* t)
        {
            assert(sizeof(void*) == sizeof(void(T::*)()));
            assert(sizeof(void*) == sizeof(T*));

            memcpy(&functionStorage[0], &fn, sizeof(void(T::*)()));
            memcpy(&instanceStorage[0], &t, sizeof(void(T::*)()));
        }

	    void operator()() const override
        {
            void(T::*fn)();
            T* t;

            memcpy(&fn, &functionStorage[0], sizeof(void(T::*)()));
            memcpy(&t, &instanceStorage[0], sizeof(void(T::*)()));
            
            (t->*fn)();
        }
    };

    struct NullCallable : public CallableBase
    {
	    void operator()() const override {}
    };

    uint8_t storage[sizeof(CallableBase)];
};

template <class ArgType>
class FunctionWithBoundArg
{
public:
    FunctionWithBoundArg()
    {
        new (storage)NullCallable();
    }

    template <class T>
    FunctionWithBoundArg(void(T::*fn)(ArgType), T* t, ArgType a)
    {
        new (storage)Callable<T>(fn, t, a);
    }

    void operator()() const
    {
        (*reinterpret_cast<const CallableBase*>(storage))();
    }

private:
    class CallableBase
    {
    public:
        virtual ~CallableBase() {}
        virtual void operator()() const = 0;

    protected:
        uint8_t functionStorage[sizeof(void*)];
        uint8_t instanceStorage[sizeof(void*)];
        uint8_t argumentStorage[sizeof(ArgType)];
    };

    template <class T>
    class Callable : public CallableBase
    {
    public:
        Callable(void(T::*fn)(ArgType), T* t, ArgType a)
        {
            assert(sizeof(void*) == sizeof(void(T::*)()));
            assert(sizeof(void*) == sizeof(T*));

            memcpy(&functionStorage[0], &fn, sizeof(void(T::*)()));
            memcpy(&instanceStorage[0], &t, sizeof(void(T::*)()));
            memcpy(&argumentStorage[0], &a, sizeof(ArgType));
        }

        void operator()() const override
        {
            void(T::*fn)(ArgType);
            T* t;
            ArgType a;

            memcpy(&fn, &functionStorage[0], sizeof(void(T::*)()));
            memcpy(&t, &instanceStorage[0], sizeof(void(T::*)()));
            memcpy(&a, &argumentStorage[0], sizeof(ArgType));

            (t->*fn)(a);
        }
    };

    struct NullCallable : public CallableBase
    {
        void operator()() const override {}
    };
    
    uint8_t __declspec(align(32)) storage[sizeof(CallableBase)];
};


template <> // special case 'void' regresses to just 'Function'
class FunctionWithBoundArg<void>
{
public:
    FunctionWithBoundArg() {}
    template <class T> FunctionWithBoundArg(void(T::*fn)(), T* t) : f(fn, t) {}
    void operator()() const { f(); }

private:
    Function f;
};
