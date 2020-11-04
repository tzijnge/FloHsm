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

      ChoiceInitGuard(&choice, ChoiceGuard_g1, &G1);

      ChoiceInitStateMachine(&choice);
    }

    std::string Log() const { return log; }

    std::string CurrentStateName() const
    {
      return ChoiceCurrentStateName(&choice);
    }

    bool g1{false};

    ChoiceInstance choice;

  private:

    static void A1(void* context) { static_cast<TestChoice*>(context)->AddToLog("A1"); }
    static void A2(void* context) { static_cast<TestChoice*>(context)->AddToLog("A2"); }
    static void A3(void* context) { static_cast<TestChoice*>(context)->AddToLog("A3"); }
    static bool G1(void* context) { return static_cast<TestChoice*>(context)->g1; }

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
    Choice_e1(&choice);
    EXPECT_EQ("A1:A3", Log());
    EXPECT_EQ("S3", CurrentStateName());
  }

  TEST_F(TestChoice, choice2)
  {
    g1 = true;
    Choice_e1(&choice);
    EXPECT_EQ("A1:A2", Log());
    EXPECT_EQ("S2", CurrentStateName());
  }
}