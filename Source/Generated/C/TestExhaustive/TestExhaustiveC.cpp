#include "gtest/gtest.h"
#include "SmExhaustive.h"
#include <string>

namespace C
{
  class TestExhaustive : public testing::Test
  {
  public:
    TestExhaustive()
    {
      //InitStateMachine();
    }

    std::string Log() const { return log; }

    std::string CurrentStateName() const
    {
      return "";
    }

  private:
    void AddToLog(const std::string& l)
    {
      if (!log.empty()) { log += ':'; }
      log += l;
    }

    std::string log;
  };

  TEST_F(TestExhaustive, bla)
  {
  }
}