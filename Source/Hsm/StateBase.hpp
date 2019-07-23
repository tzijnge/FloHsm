#pragma once
#include <stdint.h>
#include "StateId.hpp"
#include "Function.hpp"

namespace hsm
{
    class StateBase
    {
    public:
        struct TransitionDetails
        {
	        TransitionDetails()
        		: TransitionRequested(false)
        		, ToState(StateId_Invalid)
                , FromState(StateId_Invalid)
	        {}

	        bool TransitionRequested;
			StateId ToState;
            StateId FromState;
			Function TransitionAction;
        };

        virtual ~StateBase(){}
        virtual StateId GetId() const = 0;
		const TransitionDetails& GetTransitionDetails() const { return transitionDetails; };

    protected:
		TransitionDetails transitionDetails;

		void SetTransitionDetails(StateId nextState, const Function& transitionAction)
		{
			transitionDetails.TransitionRequested = true;
			transitionDetails.ToState = nextState;
            transitionDetails.FromState = GetId();
			transitionDetails.TransitionAction = transitionAction;
		}

        static bool MustCallEntry(StateId currentCompositeState, StateId fromState, StateId toState)
        {
            uint64_t ccs = static_cast<uint64_t>(currentCompositeState)& 0xFFFFFFFFFFFFFF00;
            uint64_t fs = static_cast<uint64_t>(fromState)& 0xFFFFFFFFFFFFFF00;

            if (fromState == toState && currentCompositeState == fromState)
            {
                return true;
            }

            if ((ccs & fs) == ccs && (currentCompositeState & 0xFF) == 0) // 'current composite state' is a parent state of 'from state' and is a composite state (not a leaf state)
            {
                return false;
            }

            return true;
        }

        bool MustCallExit(StateId currentCompositeState) const
        {
            uint64_t ccs = static_cast<uint64_t>(currentCompositeState)& 0xFFFFFFFFFFFFFF00;
            uint64_t ts = static_cast<uint64_t>(transitionDetails.ToState)& 0xFFFFFFFFFFFFFF00;

            if (transitionDetails.FromState == transitionDetails.ToState && currentCompositeState == transitionDetails.FromState)
            {
                return true;
            }

            if ((ccs & ts) == ccs && (currentCompositeState & 0xFF) == 0)// 'current composite state' is a parent state of 'to state' and is a composite state (not a leaf state)
            {
                return false;
            }

            return true;
        }
    };
}
