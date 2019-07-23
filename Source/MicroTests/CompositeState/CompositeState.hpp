#pragma once
#include "Hsm/StatemachineBase.hpp"
#include "Hsm/Function.hpp"
#include <new>
#include <string>


/*
@startuml
[*] --> S0

state S0{
    state S1{
        state S3{
        }
    }
    state S2{
    }
    [*] --> S1
}

S0 : entry / EntryS0
S0 : exit / ExitS0


S1 : entry / EntryS1
S1 : exit / ExitS1
S1 : E4 / A4
S1 : E8 / A8
S1 --> S3 : E2 / A2
S1 -right-> S1 : E6 / A6

S2 : entry / EntryS2
S2 : exit / ExitS2

S1 --> S2 : E0 / A0
S2 --> S1 : E1 / A1

S2 --> S2 : E7 / A7

S3 : entry / EntryS3
S3 : exit / ExitS3
S3 : E8 / A9
S3 --> S1 : E3 / A3

S0 --> [*] : E5 / A5

@enduml
*/

namespace compositestate
{
	const StateId StateId_FloHsmInitial_5OdpEA31BEcPrWrNx8u7 = 1;
    const StateId StateId_S0 = 1 << 8 | 0;
    const StateId StateId_S1 = 1 << 9 | StateId_S0 | 0;
    const StateId StateId_S2 = StateId_S0 | 1;
    const StateId StateId_S3 = StateId_S1 | 1;
    const StateId StateId_Final = 2;

    class IEvents
    {
    public:
        virtual void E0() {}
        virtual void E1() {}
        virtual void E2() {}
        virtual void E3() {}
        virtual void E4() {}
        virtual void E5() {}
        virtual void E6() {}
        virtual void E7() {}
        virtual void E8() {}
    };

    class IActions
    {
    public:
        virtual void EntryS0() = 0;
        virtual void ExitS0() = 0;
        virtual void EntryS1() = 0;
        virtual void ExitS1() = 0;
        virtual void EntryS2() = 0;
        virtual void ExitS2() = 0;
        virtual void EntryS3() = 0;
        virtual void ExitS3() = 0;
        virtual void A0() = 0;
        virtual void A1() = 0;
        virtual void A2() = 0;
        virtual void A3() = 0;
        virtual void A4() = 0;
        virtual void A5() = 0;
        virtual void A6() = 0;
        virtual void A7() = 0;
        virtual void A8() = 0;
        virtual void A9() = 0;
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

	class FloHsmInitial_5OdpEA31BEcPrWrNx8u7 : public StateBase
	{
	public:
		FloHsmInitial_5OdpEA31BEcPrWrNx8u7(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)
			: StateBase(_actions, _guards)
		{
			if (MustCallEntry(Id, fromState, toState))
			{
				SetTransitionDetails(StateId_S0, Function());
			}
		}

		virtual ~FloHsmInitial_5OdpEA31BEcPrWrNx8u7()
		{}

		StateId GetId() const override { return Id; }

	private:
		static const StateId Id = StateId_FloHsmInitial_5OdpEA31BEcPrWrNx8u7;

	};

    class S0 : public StateBase
    {
    public:
        S0(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {
            if (MustCallEntry(Id, fromState, toState))
            {
                actions->EntryS0();
                SetTransitionDetails(StateId_S1, Function());
            }
        }

        virtual ~S0()
        {
            if (MustCallExit(Id))
            {
                actions->ExitS0();
            }
        }

        StateId GetId() const override { return Id; }

    private:
        static const StateId Id = StateId_S0;
    };

    class S1 : public S0
    {
    public:
        S1(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)
            : S0(fromState, toState, _actions, _guards)
        {
            if (MustCallEntry(Id, fromState, toState))
            {
                actions->EntryS1();
            }
        }

        virtual ~S1()
        {
            if (MustCallExit(Id))
            {
                actions->ExitS1();
            }
        }

        StateId GetId() const override { return Id; }

        void E0() override
        {
            SetTransitionDetails(StateId_S2, Function(&IActions::A0, actions));
        }
        
        void E2() override
        {
            SetTransitionDetails(StateId_S3, Function(&IActions::A2, actions));
        }

        void E4() override
        {
            actions->A4();
        }

        void E6() override
        {
            SetTransitionDetails(StateId_S1, Function(&IActions::A6, actions));
        }

        void E8() override
        {
            actions->A8();
        }

    private:
        static const StateId Id = StateId_S1;
    };

    class S2 : public S0
    {
    public:
        S2(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)
            : S0(fromState, toState, _actions, _guards)
        {
            if (MustCallEntry(Id, fromState, toState))
            {
                actions->EntryS2();
            }
        }

        virtual ~S2()
        {
            if (MustCallExit(Id))
            {
                actions->ExitS2();
            }
        }

        StateId GetId() const override { return Id; }

        void E1() override
        {
            SetTransitionDetails(StateId_S1, Function(&IActions::A1, actions));
        }

        void E7() override
        {
            SetTransitionDetails(StateId_S2, Function(&IActions::A7, actions));
        }

    private:
        static const StateId Id = StateId_S2;
    };

    class S3 : public S1
    {
    public:
        S3(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)
            : S1(fromState ,toState, _actions, _guards)
        {
            if (MustCallEntry(Id, fromState, toState))
            {
                actions->EntryS3();
            }
        }

        virtual ~S3()
        {
            if (MustCallExit(Id))
            {
                actions->ExitS3();
            }
        }

        StateId GetId() const override { return Id; }

        void E3() override
        {
            SetTransitionDetails(StateId_S1, Function(&IActions::A3, actions));
        }

        void E8() override
        {
            actions->A9();
        }

    private:
        static const StateId Id = StateId_S3;
    };

    class Final : public StateBase
    {
    public:
        Final(StateId, StateId, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {}

        virtual ~Final() {}

        StateId GetId() const override { return Id; }

    private:
        static const StateId Id = StateId_Final;
    };

    class StateMachineBase : public hsm::StateMachineBase, public IEvents, private IActions, public IGuards
    {
    public:
        StateMachineBase()
            : currentState(nullptr)
        {}

		void InitStateMachine()
		{
			ChangeState(StateId_Invalid, StateId_FloHsmInitial_5OdpEA31BEcPrWrNx8u7);
			ChangeStateIfNecessary();
		}

        StateId CurrentState() const override { return currentState->GetId(); }

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

        void E4() override
        {
            currentState->E4();
            ChangeStateIfNecessary();
        }

        void E5() override
        {
            currentState->E5();
            ChangeStateIfNecessary();
        }

        void E6() override
        {
            currentState->E6();
            ChangeStateIfNecessary();
        }

        void E7() override
        {
            currentState->E7();
            ChangeStateIfNecessary();
        }

        void E8() override
        {
            currentState->E8();
            ChangeStateIfNecessary();
        }

    protected:
        StateBase* currentState;

    private:
        hsm::StateBase* ChangeStateInternal(StateId fromState, StateId toState)
        {
            StateId previousStateId = fromState;

            switch (toState)
            {
			case StateId_FloHsmInitial_5OdpEA31BEcPrWrNx8u7:
				currentState = new (stateStorage)FloHsmInitial_5OdpEA31BEcPrWrNx8u7(previousStateId, toState, this, this);
				break;
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
            case StateId_Final:
                currentState = new (stateStorage)Final(previousStateId, toState, this, this);
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
			InitStateMachine();
        }

        std::string Log() const { return log; }

    private:
        void AddToLog(const std::string& l)
        {
            if (!log.empty()) { log += ':'; }
            log += l;
        }

        void EntryS0() override { AddToLog("EntryS0"); }
        void ExitS0() override { AddToLog("ExitS0"); }
        void EntryS1() override { AddToLog("EntryS1"); }
        void ExitS1() override { AddToLog("ExitS1"); }
        void EntryS2() override { AddToLog("EntryS2"); }
        void ExitS2() override { AddToLog("ExitS2"); }
        void EntryS3() override { AddToLog("EntryS3"); }
        void ExitS3() override { AddToLog("ExitS3"); }
        void A0() override { AddToLog("A0"); }
        void A1() override { AddToLog("A1"); }
        void A2() override { AddToLog("A2"); }
        void A3() override { AddToLog("A3"); }
        void A4() override { AddToLog("A4"); }
        void A5() override { AddToLog("A5"); }
        void A6() override { AddToLog("A6"); }
        void A7() override { AddToLog("A7"); }
        void A8() override { AddToLog("A8"); }
        void A9() override { AddToLog("A9"); }

        std::string log;
    };
}