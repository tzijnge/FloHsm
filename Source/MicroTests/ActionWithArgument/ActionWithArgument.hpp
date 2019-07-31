#pragma once
#include "Hsm/StateId.hpp"
#include "Hsm/StateBase.hpp"
#include "Hsm/StateMachineBase.hpp"
#include <string>

/*
@startuml
' Integers can be specified in decimal form or hexadecimal form with '0x' prefix. Hexadecimal form is case insensitive. No exponent notation allowed
' Boolean can be specified as 'true' or 'false', case insensitive
' float can be specified in normal form. No exponent notation allowed
' string can be specified between double quotes
'
' Boundary checking is done by the parser

[*] --> S0

S0 --> S1 : E0 / A0<int32>(13)
S1 --> S2 : E0 / A0<int32>(-126)
S2 --> S3 : E0 / A0<int32>(-0xFC)
S3 --> S4 : E0 / A0<int32>(-0xfd)

S0 --> S1 : E1 / A1<bool>(true)
S1 --> S2 : E1 / A1<bool>(false)
S2 --> S3 : E1 / A1<bool>(True)
S3 --> S4 : E1 / A1<bool>(FALSE)

S0 --> S1 : E2 / A2<float>(123.456)
S1 --> S2 : E2 / A2<float>(-123.456)
S0 --> S1 : E3 / A3<string>("test123")  


@enduml
*/

namespace argument
{
    const StateId StateId_S0 = 1;
    const StateId StateId_S1 = 2;
    const StateId StateId_S2 = 3;
    const StateId StateId_S3 = 4;
    const StateId StateId_S4 = 5;

    class IEvents
    {
    public:
        virtual void E0(){}
        virtual void E1(){}
        virtual void E2(){}
        virtual void E3(){}
    };

    class IActions
    {
    public:
        virtual void A0(int32_t a) = 0;
        virtual void A1(bool a) = 0;
        virtual void A2(float a) = 0;
        virtual void A3(const char* a) = 0;
    };

    class IGuards
    {};

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

    class S0 : public StateBase
    {
    public:
        S0(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~S0()
        {}

        StateId GetId() const override
        {
            return Id;
        }

        void E0() override
        {
            actions->A0(13);
            SetTransitionDetails(StateId_S1, Function());
        }

        void E1() override
        {
            actions->A1(true);
            SetTransitionDetails(StateId_S1, Function());
        }

        void E2() override
        {
            actions->A2(123.456f);
            SetTransitionDetails(StateId_S1, Function());
        }

        void E3() override
        {
            actions->A3("test123");
            SetTransitionDetails(StateId_S1, Function());
        }

    private:
        static const StateId Id = StateId_S0;
    };

    class S1 : public StateBase
    {
    public:
        S1(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~S1()
        {}

        StateId GetId() const override
        {
            return Id;
        }

        void E0() override
        {
            actions->A0(-126);
            SetTransitionDetails(StateId_S2, Function());
        }

        void E1() override
        {
            actions->A1(false);
            SetTransitionDetails(StateId_S2, Function());
        }

        void E2() override
        {
            actions->A2(-123.456f);
            SetTransitionDetails(StateId_S2, Function());
        }

    private:
        static const StateId Id = StateId_S1;
    };

    class S2 : public StateBase
    {
    public:
        S2(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~S2()
        {}

        StateId GetId() const override
        {
            return Id;
        }

        void E0() override
        {
            actions->A0(-0xFC);
            SetTransitionDetails(StateId_S3, Function());
        }

        void E1() override
        {
            actions->A1(true);
            SetTransitionDetails(StateId_S3, Function());
        }

    private:
        static const StateId Id = StateId_S2;
    };

    class S3 : public StateBase
    {
    public:
        S3(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~S3()
        {}

        StateId GetId() const override
        {
            return Id;
        }

        void E0() override
        {
            actions->A0(-0xfd);
            SetTransitionDetails(StateId_S4, Function());
        }

        void E1() override
        {
            actions->A1(false);
            SetTransitionDetails(StateId_S4, Function());
        }

    private:
        static const StateId Id = StateId_S3;
    };

    class S4 : public StateBase
    {
    public:
        S4(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~S4()
        {}

        StateId GetId() const override
        {
            return Id;
        }

    private:
        static const StateId Id = StateId_S4;
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

        void E1() override
        {
            currentState->E1();
            ChangeStateIfNecessary();
        }

        void E2() override
        {
            currentState->E2();
            ChangeStateIfNecessary();
        }

        void E3() override
        {
            currentState->E3();
            ChangeStateIfNecessary();
        }

    protected:
        void SetInitialState()
        {
            ChangeState(StateId_Invalid, StateId_S0);
        }

        StateBase* currentState;

    private:

        hsm::StateBase* ChangeStateInternal(StateId fromState, StateId toState)
        {
            StateId previousStateId = fromState;

            switch (toState)
            {
            case StateId_S0:
                currentState = new (stateStorage)S0(previousStateId, toState, this, this);
                break;
            case StateId_S1:
                currentState = new (stateStorage)S1(previousStateId, toState, this, this);
                break;
            case StateId_S2:
                currentState = new (stateStorage)S2(previousStateId, toState, this, this);
                break;
            case StateId_S3:
                currentState = new (stateStorage)S3(previousStateId, toState, this, this);
                break;
            case StateId_S4:
                currentState = new (stateStorage)S4(previousStateId, toState, this, this);
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
        {
            SetInitialState();
        }

        ~StateMachine() override {}

        std::string Log() const { return log; }

        void A0(int32_t a) override { AddToLog("A0(" + std::to_string(a) + ")"); }
        void A1(bool a) override { AddToLog(std::string("A1(") + (a ? "true" : "false") + ")" ); }
        void A2(float a) override
        {
            std::stringstream s;
            s << "A2(" << std::fixed << std::setprecision(3) << a << ")";
            AddToLog(s.str());
        }
        void A3(const char* a) override { AddToLog(std::string("A3(" )+ a + ")"); }

    private:
        void AddToLog(const std::string& l)
        {
            if (!log.empty()) { log += ':'; }
            log += l;
        }

        std::string log;
    };
}