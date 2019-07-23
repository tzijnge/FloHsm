#pragma once

namespace exh
{
    class IGuards
    {
    public:
        virtual bool FooIsSet() const = 0;
    };

    class IActions
    {
    public:
        virtual void SetFoo() const = 0;
        virtual void ClearFoo() const = 0;
    };

    class IEvents
    {
    public:
        virtual void A() = 0;
        virtual void B() = 0;
        virtual void C() = 0;
        virtual void D() = 0;
        virtual void E() = 0;
        virtual void F() = 0;
        virtual void G() = 0;
        virtual void H() = 0;
        virtual void I() = 0;
    };
}