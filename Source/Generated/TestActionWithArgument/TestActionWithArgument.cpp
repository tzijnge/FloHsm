#include <gtest/gtest.h>
#include "StateMachine.hpp"


class TestActionWithArgument : public ::testing::Test, public StateMachine
{
public:
	TestActionWithArgument()
	{
		InitStateMachine();
	}

	std::string CurrentStateName() const
	{
		return StateNames.at(CurrentState());
	}

	~TestActionWithArgument() override {}

	std::string Log() const { return log; }

	void A0(int32_t a) override { AddToLog("A0(" + std::to_string(a) + ")"); }
	void A1(bool a) override { AddToLog(std::string("A1(") + (a ? "true" : "false") + ")"); }
	void A2(float a) override
	{
		std::stringstream s;
		s << "A2(" << std::fixed << std::setprecision(3) << a << ")";
		AddToLog(s.str());
	}
	void A3(const char* a) override { AddToLog(std::string("A3(") + a + ")"); }

private:
	void AddToLog(const std::string& l)
	{
		if (!log.empty()) { log += ':'; }
		log += l;
	}

	std::string log;
};

TEST_F(TestActionWithArgument, InitialState)
{
    EXPECT_EQ(argument::StateId_S0, CurrentStateName());
    EXPECT_EQ("", Log());
}

TEST_F(TestActionWithArgument, intArgument)
{
    EXPECT_EQ(argument::StateId_S0, CurrentStateName());
    EXPECT_EQ("", Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S1, CurrentStateName());
    EXPECT_EQ("A0(13)", Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S2, CurrentStateName());
    EXPECT_EQ("A0(13):A0(-126)", Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S3, CurrentStateName());
    EXPECT_EQ("A0(13):A0(-126):A0(-252)", Log());
    sm.E0();
    EXPECT_EQ(argument::StateId_S4, CurrentStateName());
    EXPECT_EQ("A0(13):A0(-126):A0(-252):A0(-253)", Log());
}

TEST_F(TestActionWithArgument, boolArgument)
{
    EXPECT_EQ(argument::StateId_S0, CurrentStateName());
    EXPECT_EQ("", Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S1, CurrentStateName());
    EXPECT_EQ("A1(true)", Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S2, CurrentStateName());
    EXPECT_EQ("A1(true):A1(false)", Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S3, CurrentStateName());
    EXPECT_EQ("A1(true):A1(false):A1(true)", Log());
    sm.E1();
    EXPECT_EQ(argument::StateId_S4, CurrentStateName());
    EXPECT_EQ("A1(true):A1(false):A1(true):A1(false)", Log());
}

TEST_F(TestActionWithArgument, floatArgument)
{
    EXPECT_EQ(argument::StateId_S0, CurrentStateName());
    EXPECT_EQ("", Log());
    sm.E2();
    EXPECT_EQ(argument::StateId_S1, CurrentStateName());
    EXPECT_EQ("A2(123.456)", Log());
    sm.E2();
    EXPECT_EQ(argument::StateId_S2, CurrentStateName());
    EXPECT_EQ("A2(123.456):A2(-123.456)", Log());
}

TEST_F(TestActionWithArgument, stringArgument)
{
    EXPECT_EQ(argument::StateId_S0, CurrentStateName());
    EXPECT_EQ("", Log());
    sm.E3();
    EXPECT_EQ(argument::StateId_S1, CurrentStateName());
    EXPECT_EQ("A3(test123)", Log());
}