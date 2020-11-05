#include "gtest/gtest.h"
#include "entry-exit.h"
#include <string>

namespace C
{
  class TestEntryExit : public testing::Test
  {
  public:
    TestEntryExit()
    {
      Entry_exitInitInstance(&entryExit, this);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a1, &A1);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a2, &A2);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a3, &A3);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a4, &A4);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a5, &A5);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a6, &A6);
      Entry_exitInitAction(&entryExit, Entry_exitAction_a7, &A7);
      Entry_exitInitGuard(&entryExit, Entry_exitGuard_g1, &G1);
      Entry_exitInitGuard(&entryExit, Entry_exitGuard_g2, &G2);
      Entry_exitInitStateMachine(&entryExit);
    }

    std::string Log() const { return log; }

    std::string CurrentStateName() const
    {
      return Entry_exitCurrentStateName(&entryExit);
    }

    bool g1 {false};
    bool g2 {false};

    Entry_exitInstance entryExit;

  private:

    static void A1(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A1"); }
    static void A2(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A2"); }
    static void A3(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A3"); }
    static void A4(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A4"); }
    static void A5(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A5"); }
    static void A6(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A6"); }
    static void A7(void* context) { static_cast<TestEntryExit*>(context)->AddToLog("A7"); }
    static bool G1(void* context) { return static_cast<TestEntryExit*>(context)->g1; }
    static bool G2(void* context) { return static_cast<TestEntryExit*>(context)->g2; }

    void AddToLog(const std::string& l)
    {
      if (!log.empty()) { log += ':'; }
      log += l;
    }

    std::string log;
  };

  TEST_F(TestEntryExit, initial)
  {
    EXPECT_EQ("", Log());
    EXPECT_EQ("S1", CurrentStateName());
  }

  TEST_F(TestEntryExit, useCase1)
  {
    g1 = true;
    Entry_exit_e1(&entryExit);

    EXPECT_EQ("A2:A3:A1", Log());
    EXPECT_EQ("S1", CurrentStateName());
  }

  TEST_F(TestEntryExit, useCase2)
  {
    g1 = true;
    g2 = true;
    Entry_exit_e2(&entryExit);
    Entry_exit_e1(&entryExit);

    EXPECT_EQ("A2:A4:A6:A7:A5:A1", Log());
    EXPECT_EQ("S1", CurrentStateName());
  }
}