#include "gtest/gtest.h"
#include "StateMachine.hpp"
#include <string>

class TestGenerated : public StateMachine, public testing::Test
{
public:
    TestGenerated()
        : g1(false)
        , g2(false)
        , g3(false)
    {
        InitStateMachine();
    }

    std::string Log() const { return log; }

    std::string CurrentStateName() const
    {
        return StateNames.at(CurrentState());
    }

protected:
    bool g1;
    bool g2;
    bool g3;

    void TransitionToS5()
    {
        E2();
        E1();
    }

private:
    void AddToLog(const std::string& l)
    {
        if (!log.empty()) { log += ':'; }
        log += l;
    }

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
    void A10() override { AddToLog("A10"); }
    void A11() override { AddToLog("A11"); }
    void A12() override { AddToLog("A12"); }
    void A13() override { AddToLog("A13"); }
    void A14() override { AddToLog("A14"); }
    void A15() override { AddToLog("A15"); }
    void A16() override { AddToLog("A16"); }

    bool G1() const override { return g1; }
    bool G2() const override { return g2; }
    bool G3() const override { return g3; }

    std::string log;
};

TEST_F(TestGenerated, InitialState)
{
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("A0:A1", Log());
}

TEST_F(TestGenerated, EntryGuardConditionTrue)
{
    g2 = true;
    E2();
    EXPECT_EQ("A0:A1:A2:A14", Log());
    EXPECT_EQ("S6", CurrentStateName());
}

TEST_F(TestGenerated, EntryGuardConditionFalse)
{
    g2 = false;
    E2();
    EXPECT_EQ("A0:A1:A2", Log());
    EXPECT_EQ("S6", CurrentStateName());
}

TEST_F(TestGenerated, ExitGuardConditionTrue)
{
    g1 = true;

    E2();
    E1();

    EXPECT_EQ("A0:A1:A2:A15:A16:A3:A9:A11", Log());
    EXPECT_EQ("S5", CurrentStateName());
}

TEST_F(TestGenerated, ExitGuardConditionFalse)
{
    g1 = false;

    E2();
    E1();

    EXPECT_EQ("A0:A1:A2:A16:A3:A9:A11", Log());
    EXPECT_EQ("S5", CurrentStateName());
}

TEST_F(TestGenerated, InternalTransitionOnPositiveGuardAndStateTransitionOnNegativeGuard)
{
    TransitionToS5();
    g3 = true;
    E3();

    EXPECT_EQ("A0:A1:A2:A16:A3:A9:A11:A13", Log());
    EXPECT_EQ("S5", CurrentStateName());

    g3 = false;
    E3();

    EXPECT_EQ("A0:A1:A2:A16:A3:A9:A11:A13:A12:A10:A5", Log());
    EXPECT_EQ("S3", CurrentStateName());
}

TEST_F(TestGenerated, TransitionToOtherStateWithinSameParent)
{
	E1();
	g2 = true;
	E1();
	EXPECT_EQ("A0:A1:A2:A3:A5:A6:A7:A9:A11", Log());
	EXPECT_EQ("S5", CurrentStateName());
}