#include <gtest/gtest.h>
#include "Exhaustive.hpp"

class ExhaustiveTester : public exh::ExhaustiveMachineBase
{
public:
    ExhaustiveTester()
        : setFooTimesCalled(0)
        , clearFooTimesCalled(0)
    {
        SetInitialState();
    }

    void A() override { currentState->A(); };
    void B() override {};
    void C() override {};
    void D() override {};
    void E() override {};
    void F() override {};
    void G() override {};
    void H() override {};
    void I() override {};

    int setFooTimesCalled;
    void SetFoo() const override {}
    int clearFooTimesCalled;
    void ClearFoo() const override {}
};

TEST(TestExhaustive, Initial)
{
    ExhaustiveTester sm;
    EXPECT_EQ(0, sm.setFooTimesCalled);
    EXPECT_EQ(0, sm.clearFooTimesCalled);
    EXPECT_EQ(StateId_S, sm.CurrentState());
}

TEST(TestExhaustive, A)
{
    ExhaustiveTester sm;
    sm.A();
}