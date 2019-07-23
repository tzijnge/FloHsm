#pragma once
#include "Hsm/StatemachineBase.hpp"
#include "Hsm/Function.hpp"

/*
@startuml

[*] --> S : InitialAction

S : entry / EntryAction
S : exit / ExitAction
S : E1 / A1
S : E4 [G1] / A4
S : E5 [G2] / A5
S : E5 [!G2] / A6

S --> S : E2 / A2
S --> [*] : E3 / A3

@enduml
*/

namespace singlestate
{
    const StateId StateId_S = 1;
    const StateId StateId_Final = 2;

    class IEvents
    {
    public:
        virtual void E1() {}
        virtual void E2() {}
        virtual void E3() {}
        virtual void E4() {}
        virtual void E5() {}
    };

    class IActions
    {
    public:
        virtual void InitialAction() = 0;
        virtual void EntryAction() = 0;
        virtual void ExitAction() = 0;
        virtual void A1() = 0;
        virtual void A2() = 0;
        virtual void A3() = 0;
        virtual void A4() = 0;
        virtual void A5() = 0;
        virtual void A6() = 0;
    };

    class IGuards
    {
    public:
        virtual bool G1() const = 0;
        virtual bool G2() const = 0;
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
        S(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)
            : StateBase(_actions, _guards)
        {
            if (MustCallEntry(Id, fromState, toState))
            {
                actions->EntryAction();
            }
        }

        virtual ~S()
        {
            if (MustCallExit(Id))
            {
                actions->ExitAction();
            }
        }

        StateId GetId() const override
        {
            return Id;
        }

        void E1() override { actions->A1(); }

        void E2() override
        {
            SetTransitionDetails(Id, Function(&IActions::A2, actions));
        }

        void E3() override
        {
            SetTransitionDetails(StateId_Final, Function(&IActions::A3, actions));
        }

        void E4() override
        {
            bool g1 = guards->G1();
            if (g1)
            {
                actions->A4();
            }
        }

        void E5() override
        {
            bool g2 = guards->G2();
            if (g2)
            {
                actions->A5();
            }
            else
            {
                actions->A6();
            }
        }

    private:
        static const StateId Id = StateId_S;
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
        class Event
        {
        public:
            Event(void(IEvents::*_eventAction)())
                : next(nullptr)
                , eventAction(_eventAction)
            {}

            virtual void ExecuteOn(IEvents* events)
            {
                (events->*eventAction)();
            }

            Event* next;

        private:
            void(IEvents::*eventAction)();
        };

    public:
        StateMachineBase()
            : currentState(nullptr)
            , currentEvent(nullptr)
            , lastEvent(nullptr)
        {}

        StateId CurrentState() const override
        {
            return currentState->GetId();
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

    protected:
        void SetInitialState()
        {
            ChangeState(StateId_Invalid, StateId_S);
        }

        StateBase* currentState;

    private:
        void ExecuteEvent(Event* eventToExecute)
        {
            if (currentEvent == nullptr)
            {
                currentEvent = eventToExecute;
                lastEvent = currentEvent;
            }
            else
            {
                Event* event = currentEvent;
                while (event != nullptr)
                {
                    if (event == eventToExecute) { return; }
                    event = event->next;
                }

                lastEvent->next = eventToExecute;
                lastEvent = lastEvent->next;
                // must return here as well?
            }

            while (currentEvent != nullptr)
            {
                currentEvent->ExecuteOn(currentState);
                currentEvent = currentEvent->next;
            }
        }

        hsm::StateBase* ChangeStateInternal(StateId fromState, StateId toState)
        {
            StateId previousStateId = fromState;

            switch (toState)
            {
            case StateId_S:
                currentState = new (stateStorage)S(previousStateId, toState, this, this);
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
        Event* currentEvent;
        Event* lastEvent;
    };

    class StateMachine : public StateMachineBase
    {
    public:
        StateMachine()
            : guard1(false)
            , guard2(false)
        {
            StateMachine::InitialAction();
            SetInitialState();
        }

        std::string Log() const { return log; }
        void SetGuard1(bool guard) { guard1 = guard; }
        void SetGuard2(bool guard) { guard2 = guard; }

    private:
        void AddToLog(const std::string& l)
        {
            if (!log.empty()) { log += ':'; }
            log += l;
        }

        void InitialAction() override {AddToLog("Initial"); }
        void EntryAction() override { AddToLog("Entry"); }
        void ExitAction() override { AddToLog("Exit"); }
        void A1() override { AddToLog("A1"); }
        void A2() override { AddToLog("A2"); }
        void A3() override { AddToLog("A3"); }
        void A4() override { AddToLog("A4"); }
        void A5() override { AddToLog("A5"); }
        void A6() override { AddToLog("A6"); }

        bool G1() const override { return guard1; }
        bool G2() const override { return guard2; }
        
        std::string log;
        bool guard1;
        bool guard2;
    };
}