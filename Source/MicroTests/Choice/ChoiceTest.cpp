#include <gtest/gtest.h>
#include "Choice.hpp"

class ChoiceTest : public ::testing::Test
{
protected:
    choice::StateMachine sm;
};

TEST_F(ChoiceTest, InitialState)
{
    EXPECT_EQ(choice::StateId_S, sm.CurrentState());
    EXPECT_EQ("", sm.Log());
}

TEST_F(ChoiceTest, GuardIsSet)
{
    sm.SetG0(true);
    sm.E0();
    EXPECT_EQ(choice::StateId_S, sm.CurrentState());
    EXPECT_EQ("A0", sm.Log());
}

TEST_F(ChoiceTest, GuardIsNotSet)
{
    sm.SetG0(false);
    sm.E0();
    EXPECT_EQ(choice::StateId_S, sm.CurrentState());
    EXPECT_EQ("A1", sm.Log());
}