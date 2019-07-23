#pragma once
#include "Hsm/StateBase.hpp"
#include "ExhaustiveStateIds.hpp"
#include "ExhaustiveInterfaces.hpp"
#include <iostream>

const StateId StateId_T0 = 100;

const StateId StateId_S = 1;
const StateId StateId_S1 = 2;
const StateId StateId_S2 = 3;
const StateId StateId_S11 = 4;
const StateId StateId_S21 = 5;
const StateId StateId_S211 = 6;

namespace exh
{
    class ExhaustiveStateBase : public hsm::StateBase, public IEvents
    {
    public:
        ExhaustiveStateBase(IActions* _actions)
            : actions(_actions)
        {}

    protected:
        IActions* actions;
    };

    class S : public ExhaustiveStateBase
    {
    public:
        S(StateId previousState, IActions* _actions)
            : ExhaustiveStateBase(_actions)
        {
            if (MustCallEntry(Id, previousState, StateId_Invalid))
            {}
        }

        ~S()
        {
            if (MustCallExit(Id))
            {}
        }

        StateId GetId() const override { return Id; }

        void A() override { actions->SetFoo(); }
        void B() override {}
        void C() override {}
        void D() override {}
        void E() override {}
        void F() override {}
        void G() override {}
        void H() override {}
        void I() override {}

    private:
        static const StateId Id = StateId_S;
    };
}