#include "gtest/gtest.h"
#include "Hsm/Function.hpp"


class FunctionTest : public testing::Test
{
public:
    FunctionTest()
        : TestActionTimesCalled(0)
    {}

    int32_t TestActionTimesCalled;
    std::string TestAction2Arguments;

    void TestAction()
    {
        TestActionTimesCalled++;
    }

    void TestAction2(int i)
    {
        TestAction2Arguments += std::to_string(i) + ":";
    }

    void TestAction3(bool b)
    {
        TestAction2Arguments += std::to_string(b) + ":";
    }

    void TestAction4(float f)
    {
      std::stringstream ss;
      ss << std::fixed << std::setprecision(3) << f;
      TestAction2Arguments += ss.str() + ":";
    }

    void TestAction5(const char* s)
    {
        TestAction2Arguments += std::string(s) + ":";
    }

    void TestAction6(double d)
    {
        TestAction2Arguments += std::to_string(d) + ":";
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

TEST_F(FunctionTest, Function2_WithArgument2)
{
    Function f1(&FunctionTest::TestAction2, This(), 13);
    Function f2(&FunctionTest::TestAction2, This(), 123);
    Function f3(&FunctionTest::TestAction3, This(), true);
    Function f4(&FunctionTest::TestAction4, This(), 123.456f);
    Function f5(&FunctionTest::TestAction5, This(), "Test123");

    EXPECT_EQ("", TestAction2Arguments);
    f1();
    EXPECT_EQ("13:", TestAction2Arguments);
    f2();
    EXPECT_EQ("13:123:", TestAction2Arguments);
    f3();
    EXPECT_EQ("13:123:1:", TestAction2Arguments);
    f4();
    EXPECT_EQ("13:123:1:123.456:", TestAction2Arguments);
    f5();
    EXPECT_EQ("13:123:1:123.456:Test123:", TestAction2Arguments);
}

TEST_F(FunctionTest, Function2_WithArgument3)
{
    Function f1(&FunctionTest::TestAction, This());
    Function f2(&FunctionTest::TestAction, This());

    EXPECT_EQ(0, TestActionTimesCalled);
    f1();
    EXPECT_EQ(1, TestActionTimesCalled);
    f2();
    EXPECT_EQ(2, TestActionTimesCalled);
}
