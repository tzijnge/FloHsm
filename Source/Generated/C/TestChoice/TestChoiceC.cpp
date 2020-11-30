#include "gtest/gtest.h"
#include "choice.h"
#include <string>

namespace C
{
  class TestChoice : public testing::Test
  {
  public:
    TestChoice()
    {
      ChoiceInitInstance(&choice, this);
      ChoiceInitAction(&choice, ChoiceAction_a1, &A1);
      ChoiceInitAction(&choice, ChoiceAction_a2, &A2);
      ChoiceInitAction(&choice, ChoiceAction_a3, &A3);
      ChoiceInitAction(&choice, ChoiceAction_a4, &A4);
      ChoiceInitAction(&choice, ChoiceAction_a5, &A5);

      ChoiceInitGuard(&choice, ChoiceGuard_g1, &G1);
      ChoiceInitGuard(&choice, ChoiceGuard_g2, &G2);

      ChoiceInitStateMachine(&choice);
    }

    std::string Log() const { return log; }

    std::string CurrentStateName() const
    {
      return ChoiceCurrentStateName(&choice);
    }

    bool g1{false};
    bool g2{false};

    ChoiceInstance choice;

  private:

    static void A1(void* context) { static_cast<TestChoice*>(context)->AddToLog("A1"); }
    static void A2(void* context) { static_cast<TestChoice*>(context)->AddToLog("A2"); }
    static void A3(void* context) { static_cast<TestChoice*>(context)->AddToLog("A3"); }
    static void A4(void* context) { static_cast<TestChoice*>(context)->AddToLog("A4"); }
    static void A5(void* context) { static_cast<TestChoice*>(context)->AddToLog("A5"); }
    static bool G1(const void* context) { return static_cast<const TestChoice*>(context)->g1; }
    static bool G2(const void* context) { return static_cast<const TestChoice*>(context)->g2; }

    void AddToLog(const std::string& l)
    {
      if (!log.empty()) { log += ':'; }
      log += l;
    }

    std::string log;
  };

  TEST_F(TestChoice, choice1)
  {
    g1 = false;
    g2 = false;
    Choice_e1(&choice);
    EXPECT_EQ("A1:A3:A5", Log());
    EXPECT_EQ("S3", CurrentStateName());
  }

  TEST_F(TestChoice, choice2)
  {
    g1 = false;
    g2 = true;
    Choice_e1(&choice);
    EXPECT_EQ("A1:A3:A4", Log());
    EXPECT_EQ("S2", CurrentStateName());
  }

  TEST_F(TestChoice, choice3)
  {
    g1 = true;
    Choice_e1(&choice);
    EXPECT_EQ("A1:A2", Log());
    EXPECT_EQ("S2", CurrentStateName());
  }
}