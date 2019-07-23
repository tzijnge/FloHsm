#include <gtest/gtest.h>
#include "SingleState.hpp"
#include <functional>

class SingleStateTest : public ::testing::Test
{
protected:
    singlestate::StateMachine sm;
};

TEST_F(SingleStateTest, InitialState)
{
    EXPECT_EQ(singlestate::StateId_S, sm.CurrentState());
}

TEST_F(SingleStateTest, InitialActionAndEntryActionExecuted)
{
    EXPECT_EQ("Initial:Entry", sm.Log());
}

TEST_F(SingleStateTest, ActionExecutedOnInternalEvent)
{
    sm.E1();
    EXPECT_EQ("Initial:Entry:A1", sm.Log());
    EXPECT_EQ(singlestate::StateId_S, sm.CurrentState());
}

TEST_F(SingleStateTest, ActionExecutedTwice)
{
    sm.E1();
    sm.E1();
    EXPECT_EQ("Initial:Entry:A1:A1", sm.Log());
    EXPECT_EQ(singlestate::StateId_S, sm.CurrentState());
}

TEST_F(SingleStateTest, TransitionToSelf)
{
    sm.E2();
    EXPECT_EQ("Initial:Entry:Exit:A2:Entry", sm.Log());
    EXPECT_EQ(singlestate::StateId_S, sm.CurrentState());
}

TEST_F(SingleStateTest, TransitionToFinalState)
{
    sm.E3();
    EXPECT_EQ("Initial:Entry:Exit:A3", sm.Log());
    EXPECT_EQ(singlestate::StateId_Final, sm.CurrentState());
}

TEST_F(SingleStateTest, NoActionsExecutedInFinalState)
{
    sm.E3();
    EXPECT_EQ("Initial:Entry:Exit:A3", sm.Log());
    EXPECT_EQ(singlestate::StateId_Final, sm.CurrentState());
    sm.E1();
    sm.E2();
    sm.E3();
    EXPECT_EQ("Initial:Entry:Exit:A3", sm.Log());
    EXPECT_EQ(singlestate::StateId_Final, sm.CurrentState());
}

TEST_F(SingleStateTest, ActionOrNoActionDependingOnGuard)
{
    sm.SetGuard1(false);
    sm.E4();
    EXPECT_EQ("Initial:Entry", sm.Log());
    
    sm.SetGuard1(true);
    sm.E4();
    EXPECT_EQ("Initial:Entry:A4", sm.Log());
    
    sm.SetGuard1(false);
    sm.E4();
    EXPECT_EQ("Initial:Entry:A4", sm.Log());

    EXPECT_EQ(singlestate::StateId_S, sm.CurrentState());
}

TEST_F(SingleStateTest, ActionOrOtherActionDependingOnGuard)
{
    sm.SetGuard2(true);
    sm.E5();
    EXPECT_EQ("Initial:Entry:A5", sm.Log());

    sm.SetGuard2(false);
    sm.E5();
    EXPECT_EQ("Initial:Entry:A5:A6", sm.Log());

    EXPECT_EQ(singlestate::StateId_S, sm.CurrentState());
}