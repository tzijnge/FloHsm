#include "gtest\gtest.h"
#include "Hsm\Function.hpp"


class FunctionTest : public testing::Test
{
public:
    FunctionTest()
        : TestActionTimesCalled(0)
    {}

    int TestActionTimesCalled;
    std::string TestAction2Arguments;

    void TestAction()
    {
        TestActionTimesCalled++;
    }

    void TestAction2(int i)
    {
        TestAction2Arguments += std::to_string(i) + ":";
    }

    FunctionTest* This()
    {
        return this;
    }
};

TEST_F(FunctionTest, DefaultConstructor)
{
    Function f;
    f(); // no action
}

TEST_F(FunctionTest, WrapMemberFunctionInObject)
{
    Function f(&FunctionTest::TestAction, This());
    EXPECT_EQ(0, TestActionTimesCalled);
    f();
    EXPECT_EQ(1, TestActionTimesCalled);
}

TEST_F(FunctionTest, Copy)
{
    Function f1(&FunctionTest::TestAction, This());
    Function f2(f1);
    EXPECT_EQ(0, TestActionTimesCalled);
    f1();
    EXPECT_EQ(1, TestActionTimesCalled);
    f2();
    EXPECT_EQ(2, TestActionTimesCalled);
}

TEST_F(FunctionTest, Assignment)
{
    Function f1(&FunctionTest::TestAction, This());
    Function f2 = f1;
    Function f3;
    f3 = f2;
    EXPECT_EQ(0, TestActionTimesCalled);
    f1();
    EXPECT_EQ(1, TestActionTimesCalled);
    f2();
    EXPECT_EQ(2, TestActionTimesCalled);
    f3();
    EXPECT_EQ(3, TestActionTimesCalled);
}

TEST_F(FunctionTest, Function2_Void)
{
    FunctionWithBoundArg<void> f(&FunctionTest::TestAction, This());
    
    EXPECT_EQ(0, TestActionTimesCalled);
    f();
    EXPECT_EQ(1, TestActionTimesCalled);
    f();
    EXPECT_EQ(2, TestActionTimesCalled);
}

TEST_F(FunctionTest, Function2_WithArgument)
{
    FunctionWithBoundArg<int> f1(&FunctionTest::TestAction2, This(), 13);
    FunctionWithBoundArg<int> f2(&FunctionTest::TestAction2, This(), 123);

    EXPECT_EQ("", TestAction2Arguments);
    f1();
    EXPECT_EQ("13:", TestAction2Arguments);
    f2();
    EXPECT_EQ("13:123:", TestAction2Arguments);
}