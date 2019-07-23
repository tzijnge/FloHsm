#pragma once
#include "StateBase.hpp"
#include "StateId.hpp"

namespace hsm
{
    class StateMachineBase
    {
    public:
        StateMachineBase()
            : currentState(nullptr)
        {}

        virtual ~StateMachineBase() {}

    protected:
        void ChangeStateIfNecessary()
        {
            StateBase::TransitionDetails transition = currentState->GetTransitionDetails();
            while (transition.TransitionRequested)
            {
                ChangeState(transition.FromState, transition.ToState, transition.TransitionAction);
                transition = currentState->GetTransitionDetails();
            }
        }

        void ChangeState(StateId fromState, StateId toState)
        {
            static Function f;
            ChangeState(fromState, toState, f);
        }

        void ChangeState(StateId fromState, StateId toState, const Function& transitionAction)
        {
            if (currentState != nullptr)
            {
                currentState->~StateBase();
            }

            transitionAction();

            currentState = ChangeStateInternal(fromState, toState);
        }

        virtual StateId CurrentState() const = 0;
        virtual StateBase* ChangeStateInternal(StateId fromState, StateId toState) = 0;

    private:

        StateBase* currentState;
    };
}