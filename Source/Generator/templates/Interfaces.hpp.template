#pragma once

namespace
{
class IGuards
{
public:
    virtual ~IGuards() {}
% for g in guard_names:
    virtual bool ${g}() const = 0;
% endfor
};

class IActions
{
public:
    virtual ~IActions() {}
% for a in action_prototypes:
    virtual ${a} = 0;
% endfor
};

class IEvents
{
public:
    virtual ~IEvents() {}
% for e in event_names:
    virtual void ${e}() {}
% endfor
};

}