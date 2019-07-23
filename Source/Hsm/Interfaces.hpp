#pragma once

class IGuards
{
public:
    virtual bool MyGuard() const = 0;
};

class IActions
{
public:
    virtual void MyAction() const = 0;
    virtual void MyAction2() const = 0;
};

class IEvents
{
public:
    virtual void MyEvent() = 0;
};