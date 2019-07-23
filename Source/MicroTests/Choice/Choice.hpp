#pragma once
#include "Hsm/StatemachineBase.hpp"
#include "Hsm/Function.hpp"

/*
@startuml
[*] --> S

state choice1 <<choice>>

S --> choice1 : E0
choice1 --> S : [G0] / A0
choice1 --> S : [!G0] / A1


@enduml
*/

namespace choice
{
    const StateId StateId_S = 1;
    const StateId StateId_Choice0 = 2;

    class IEvents
    {
    public:
        virtual void E0(){};
    };

    class IActions
    {
    public:
        virtual void A0() = 0;
        virtual void A1() = 0;
    };

    class IGuards
    {
    public:
        virtual bool G0() const  = 0;
    };

    class StateBase : public hsm::StateBase, public IEvents
    {
    public:
        StateBase(IActions* _actions, IGuards* _guards)
            : actions(_actions)
            , guards(_guards)
        {}

        virtual ~StateBase(){}

    protected:
        IActions* actions;
        IGuards* guards;
    };

    class S : public StateBase
    {
    public:
        S(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~S()
        {}

        StateId GetId() const override
        {
            return Id;
        }

        void E0() override
        {
            SetTransitionDetails(StateId_Choice0, Function());
        }

    private:
        static const StateId Id = StateId_S;
    };

    class Choice0 : public StateBase
    {
    public:
        Choice0(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {
            bool g0 = guards->G0();
            if (g0)
            {
                SetTransitionDetails(StateId_S, Function(&IActions::A0, actions));
            }
            else
            {
                SetTransitionDetails(StateId_S, Function(&IActions::A1, actions));
            }
        }

        virtual ~Choice0()
        {}

        StateId GetId() const override
        {
            return Id;
        }

    private:
        static const StateId Id = StateId_Choice0;
    };

    class StateMachineBase : public hsm::StateMachineBase, public IEvents, private IActions, public IGuards
    {
    public:
        StateMachineBase()
            : currentState(nullptr)
        {}

        StateId CurrentState() const override
        {
            return currentState->GetId();
        }

        void E0() override
        {
            currentState->E0();
            ChangeStateIfNecessary();
        }
        
    protected:
        void SetInitialState()
        {
            ChangeState(StateId_Invalid, StateId_S);
        }

        StateBase* currentState;

    private:

        hsm::StateBase* ChangeStateInternal(StateId fromState, StateId toState)
        {
            StateId previousStateId = fromState;

            switch (toState)
            {
            case StateId_S:
                currentState = new (stateStorage)S(previousStateId, toState, this, this);
                break;
            case StateId_Choice0:
                currentState = new (stateStorage)Choice0(previousStateId, toState, this, this);
                break;
            default:
                break;
            }

            return currentState;
        }

        uint8_t stateStorage[1000];
    };

    class StateMachine : public StateMachineBase
    {
    public:
        StateMachine()
            : g0(false)
        {
            SetInitialState();
        }

        ~StateMachine() override {}

        void SetG0(bool value)
        {
            g0 = value;
        }

        std::string Log() const { return log; }

        void A0() override { AddToLog("A0"); }
        void A1() override { AddToLog("A1"); }
        bool G0() const override { return g0; }

    private:
        void AddToLog(const std::string& l)
        {
            if (!log.empty()) { log += ':'; }
            log += l;
        }

        std::string log;
        bool g0;
    };
}