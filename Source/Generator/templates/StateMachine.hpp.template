#pragma once
#include "Interfaces.hpp"
#include "StateIds.hpp"
#include "States.hpp"
#include "Hsm/StateMachineBase.hpp"

namespace
{
class StateMachine: public hsm::StateMachineBase, public IEvents, private IActions, public IGuards
{
public:
    StateMachine()
        : currentState(nullptr)
    {}

    void InitStateMachine()
    {
        ChangeState(StateId_Invalid, StateId_FloHsmInitial_5OdpEA31BEcPrWrNx8u7);
        ChangeStateIfNecessary();
    }

    StateId CurrentState() const override { return currentState->GetId(); }

    % for e in events:
    void ${e}() override
    {
        currentState->${e}();
        ChangeStateIfNecessary();
    }
    
    % endfor

protected:
    StateBase* currentState;

private:
    StateBase* ChangeStateInternal(StateId fromState, StateId toState) override
    {
        const StateId previousStateId = fromState;

        switch (toState)
        {
        % for s in states:
        case StateId_${s}:
            currentState = new (stateStorage)${s}(previousStateId, toState, this, this);
            break;
        % endfor
        default:
            break;
        }

        return currentState;
    }

    uint8_t stateStorage[1000];
};
}