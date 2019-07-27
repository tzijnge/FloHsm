#include <gtest/gtest.h>
#include "StateMachine.hpp"
#include <functional>

class SingleStateTest : public StateMachine, public ::testing::Test
{
public:
	SingleStateTest()
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

private:
	void AddToLog(const std::string& message)
	{
		if (!log.empty()) { log += ':'; }
		log += message;
	}

	void A0() override { AddToLog("Initial"); }
	void A1() override { AddToLog("A1"); }
	void A2() override { AddToLog("A2"); }
	void A3() override { AddToLog("A3"); }
	void A4() override { AddToLog("A4"); }
	void A5() override { AddToLog("A5"); }
	void A6() override { AddToLog("A6"); }
	void EntryAction() override { AddToLog("Entry"); }
	void ExitAction() override { AddToLog("Exit"); }


	bool G1() const override { return g1; }
	bool G2() const override { return g2; }

	std::string log;
};

TEST_F(SingleStateTest, InitialState)
{
    EXPECT_EQ("S", CurrentStateName());
}

TEST_F(SingleStateTest, InitialActionAndEntryActionExecuted)
{
    EXPECT_EQ("Initial:Entry", Log());
}

TEST_F(SingleStateTest, ActionExecutedOnInternalEvent)
{
    E1();
    EXPECT_EQ("Initial:Entry:A1", Log());
    EXPECT_EQ("S", CurrentStateName());
}

TEST_F(SingleStateTest, ActionExecutedTwice)
{
    E1();
    E1();
    EXPECT_EQ("Initial:Entry:A1:A1", Log());
    EXPECT_EQ("S", CurrentStateName());
}

TEST_F(SingleStateTest, TransitionToSelf)
{
    E2();
    EXPECT_EQ("Initial:Entry:Exit:A2:Entry", Log());
    EXPECT_EQ("S", CurrentStateName());
}

TEST_F(SingleStateTest, TransitionToFinalState)
{
    E3();
    EXPECT_EQ("Initial:Entry:Exit:A3", Log());
    EXPECT_EQ("FloHsmFinal_5OdpEA31BEcPrWrNx8u7", CurrentStateName());
}

TEST_F(SingleStateTest, NoActionsExecutedInFinalState)
{
    E3();
    EXPECT_EQ("Initial:Entry:Exit:A3", Log());
    EXPECT_EQ("FloHsmFinal_5OdpEA31BEcPrWrNx8u7", CurrentStateName());
    E1();
    E2();
    E3();
    EXPECT_EQ("Initial:Entry:Exit:A3", Log());
    EXPECT_EQ("FloHsmFinal_5OdpEA31BEcPrWrNx8u7", CurrentStateName());
}

TEST_F(SingleStateTest, ActionOrNoActionDependingOnGuard)
{
    g1 = false;
    E4();
    EXPECT_EQ("Initial:Entry", Log());
    
    g1 = true;
    E4();
    EXPECT_EQ("Initial:Entry:A4", Log());
    
    g1 = false;
    E4();
    EXPECT_EQ("Initial:Entry:A4", Log());

    EXPECT_EQ("S", CurrentStateName());
}

TEST_F(SingleStateTest, ActionOrOtherActionDependingOnGuard)
{
    g2 = true;
    E5();
    EXPECT_EQ("Initial:Entry:A5", Log());

    g2 = false;
    E5();
    EXPECT_EQ("Initial:Entry:A5:A6", Log());

    EXPECT_EQ("S", CurrentStateName());
}