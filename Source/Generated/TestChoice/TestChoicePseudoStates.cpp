#include "gtest/gtest.h"
#include "StateMachine.hpp"
#include <string>

class TestChoicePseudoStates : public StateMachine, public testing::Test
{
public:
	TestChoicePseudoStates()
		: g1(false)
		, g2(false)
		, g3(false)
	{}

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
	void AddToLog(const std::string& l)
	{
		if (!log.empty()) { log += ':'; }
		log += l;
	}

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

	bool G1() const override { return g1; }
	bool G2() const override { return g2; }
	bool G3() const override { return g3; }

	std::string log;
};

class TestInitialS1 : public TestChoicePseudoStates
{
public:
	TestInitialS1()
	{
		g1 = true;
		g2 = true;
		InitStateMachine();
	}
};

class TestInitialS2 : public TestChoicePseudoStates
{
public:
	TestInitialS2()
	{
		g1 = true;
		InitStateMachine();
	}
};

class TestInitialS3 : public TestChoicePseudoStates
{
public:
	TestInitialS3()
	{
		InitStateMachine();
	}
};

TEST_F(TestInitialS3, Initial)
{
	g1 = false;
	g2 = false;
	EXPECT_EQ("s3", CurrentStateName());
	EXPECT_EQ("A8:A5", Log());
}

TEST_F(TestInitialS2, Initial)
{
	g1 = true;
	g2 = false;
	EXPECT_EQ("s2", CurrentStateName());
	EXPECT_EQ("A7:A1:A3", Log());
}

TEST_F(TestInitialS1, Initial)
{
	g1 = true;
	g2 = true;
	EXPECT_EQ("s1", CurrentStateName());
	EXPECT_EQ("A6:A1", Log());
}

TEST_F(TestInitialS2, NestedChoice1)
{
	g3 = false;
	e1();
	EXPECT_EQ("s4", CurrentStateName());
	EXPECT_EQ("A7:A1:A3:A4:A2:A10:A5", Log());
}

TEST_F(TestInitialS2, NestedChoice2)
{
	g3 = true;
	e1();
	EXPECT_EQ("s1", CurrentStateName());
	EXPECT_EQ("A7:A1:A3:A4:A9", Log());
}