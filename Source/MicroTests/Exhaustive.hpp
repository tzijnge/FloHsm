#pragma once
#include "Hsm/StateMachineBase.hpp"
#include "ExhaustiveStates.hpp"
#include <iostream>

namespace exh
{
    class ExhaustiveMachineBase : public hsm::StateMachineBase, public IEvents, public IActions
    {
        class Event
        {
        public:
            Event(void(IEvents::*_eventAction)())
                : eventAction(_eventAction)
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
        ExhaustiveMachineBase()
            : currentEvent(nullptr)
            , lastEvent(nullptr)
            , currentState(nullptr)
        {}

        void A() override
        {
            static Event event(&IEvents::A);
            ExecuteEvent(&event);
        }

        StateId CurrentState() const override
        {
            return currentState->GetId();
        }

    protected:
        void SetInitialState()
        {
            //toState = StateId_S;
            //ChangeState(,,);
        }

        ExhaustiveStateBase* currentState;

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
                currentState = new (stateStorage)S(previousStateId, this);
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
}
