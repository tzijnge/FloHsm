#pragma once

namespace
{
class IGuards
{
public:
    virtual ~IGuards() {}
    virtual bool G2() const = 0;
    virtual bool G1() const = 0;
    virtual bool G3() const = 0;
};

class IActions
{
public:
    virtual ~IActions() {}
    virtual void A7() = 0;
    virtual void A8() = 0;
    virtual void A10() = 0;
    virtual void A6() = 0;
    virtual void A9() = 0;
    virtual void A3() = 0;
    virtual void A4() = 0;
    virtual void A2() = 0;
    virtual void A5() = 0;
    virtual void A1() = 0;
};

class IEvents
{
public:
    virtual ~IEvents() {}
    virtual void e1() {}
};

}