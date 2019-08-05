#include <gtest/gtest.h>
#include "StateMachine.hpp"
#include <functional>

class TestCompositeState : public StateMachine, public testing::Test
{
public:
	TestCompositeState()
	{
		InitStateMachine();
	}

	std::string Log() const { return log; }

	std::string CurrentStateName() const
	{
		return StateNames.at(CurrentState());
	}

private:
	void AddToLog(const std::string& l)
	{
		if (!log.empty()) { log += ':'; }
		log += l;
	}

	void EntryS0() override { AddToLog("EntryS0"); }
	void ExitS0() override { AddToLog("ExitS0"); }
	void EntryS1() override { AddToLog("EntryS1"); }
	void ExitS1() override { AddToLog("ExitS1"); }
	void EntryS2() override { AddToLog("EntryS2"); }
	void ExitS2() override { AddToLog("ExitS2"); }
	void EntryS3() override { AddToLog("EntryS3"); }
	void ExitS3() override { AddToLog("ExitS3"); }
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

	std::string log;
};

TEST_F(TestCompositeState, InitialState)
{
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1", Log());
}

TEST_F(TestCompositeState, Event0)
{
    E0();
    EXPECT_EQ("S2", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A0:EntryS2", Log());
}

TEST_F(TestCompositeState, Event1)
{
    E0();
    E1();
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A0:EntryS2:ExitS2:A1:EntryS1", Log());
}

TEST_F(TestCompositeState, Event2)
{
    E2();
    EXPECT_EQ("S3", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3", Log());
}

TEST_F(TestCompositeState, Event3)
{
    E2();
    E3();
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:ExitS3:A3", Log());
}

TEST_F(TestCompositeState, Event0InS3)
{
    E2();
    E0();
    EXPECT_EQ("S2", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:ExitS3:ExitS1:A0:EntryS2", Log());
}

TEST_F(TestCompositeState, Event6_TransitionToSelfOnCompositeState)
{
    E6();
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A6:EntryS1", Log());
}

TEST_F(TestCompositeState, Event7_TransitionToSelfOnLeafState)
{
    E0();
    E7();
    EXPECT_EQ("S2", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A0:EntryS2:ExitS2:A7:EntryS2", Log());
}

TEST_F(TestCompositeState, Event4InS1)
{
    E4();
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A4", Log());
}

TEST_F(TestCompositeState, Event4InS3)
{
    E2();
    E4();
    EXPECT_EQ("S3", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:A4", Log());
}

TEST_F(TestCompositeState, Event8InS1)
{
    E8();
    EXPECT_EQ("S1", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A8", Log());
}

TEST_F(TestCompositeState, Event8InS3)
{
    E2();
    E8();
    EXPECT_EQ("S3", CurrentStateName());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:A9", Log());
}