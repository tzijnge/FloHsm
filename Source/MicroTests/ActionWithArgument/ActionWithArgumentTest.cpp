#include <gtest/gtest.h>
#include "ActionWithArgument.hpp"

class ActionWithArgumentTest : public ::testing::Test
{
protected:
    argument::StateMachine sm;
};

TEST_F(ActionWithArgumentTest, InitialState)
{
    EXPECT_EQ(argument::StateId_S0, sm.CurrentState());
    EXPECT_EQ("", sm.Log());
}

TEST_F(ActionWithArgumentTest, intArgument)
{
    EXPECT_EQ(argument::StateId_S0, sm.CurrentState());
    EXPECT_EQ("", sm.Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S1, sm.CurrentState());
    EXPECT_EQ("A0(13)", sm.Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S2, sm.CurrentState());
    EXPECT_EQ("A0(13):A0(-126)", sm.Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S3, sm.CurrentState());
    EXPECT_EQ("A0(13):A0(-126):A0(-252)", sm.Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S4, sm.CurrentState());
    EXPECT_EQ("A0(13):A0(-126):A0(-252):A0(-253)", sm.Log());
}

TEST_F(ActionWithArgumentTest, boolArgument)
{
    EXPECT_EQ(argument::StateId_S0, sm.CurrentState());
    EXPECT_EQ("", sm.Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S1, sm.CurrentState());
    EXPECT_EQ("A1(true)", sm.Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S2, sm.CurrentState());
    EXPECT_EQ("A1(true):A1(false)", sm.Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S3, sm.CurrentState());
    EXPECT_EQ("A1(true):A1(false):A1(true)", sm.Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S4, sm.CurrentState());
    EXPECT_EQ("A1(true):A1(false):A1(true):A1(false)", sm.Log());
}

TEST_F(ActionWithArgumentTest, floatArgument)
{
    EXPECT_EQ(argument::StateId_S0, sm.CurrentState());
    EXPECT_EQ("", sm.Log());
    sm.E2();
    EXPECT_EQ(argument::StateId_S1, sm.CurrentState());
    EXPECT_EQ("A2(123.456)", sm.Log());
    sm.E2();
    EXPECT_EQ(argument::StateId_S2, sm.CurrentState());
    EXPECT_EQ("A2(123.456):A2(-123.456)", sm.Log());
}

TEST_F(ActionWithArgumentTest, stringArgument)
{
    EXPECT_EQ(argument::StateId_S0, sm.CurrentState());
    EXPECT_EQ("", sm.Log());
    sm.E3();
    EXPECT_EQ(argument::StateId_S1, sm.CurrentState());
    EXPECT_EQ("A3(test123)", sm.Log());
}