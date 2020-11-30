#include "gtest/gtest.h"
#include "SmUart.h"
#include <string>

namespace C
{
  class TestUart : public testing::Test
  {
  public:
    TestUart()
    {
      SmUartInitInstance(&smUart, this);
      SmUartInitAction(&smUart, SmUartAction_configureHw, &configureHw);
      SmUartInitAction(&smUart, SmUartAction_saveConfig, &saveConfig);
      SmUartInitAction(&smUart, SmUartAction_setError, &setError);
      SmUartInitAction(&smUart, SmUartAction_stopHw, &stopHw);
      SmUartInitAction(&smUart, SmUartAction_startHw, &startHw);

      SmUartInitGuard(&smUart, SmUartGuard_configOk, &ConfigOk);

      SmUartInitStateMachine(&smUart);
    }

    std::string Log() const { return log; }

    std::string CurrentStateName() const
    {
      return SmUartCurrentStateName(&smUart);
    }

    bool configOk{false};

    SmUartInstance smUart;

  private:

    static void configureHw(void* context) { static_cast<TestUart*>(context)->AddToLog("configureHw"); }
    static void saveConfig(void* context) { static_cast<TestUart*>(context)->AddToLog("saveConfig"); }
    static void setError(void* context) { static_cast<TestUart*>(context)->AddToLog("setError"); }
    static void stopHw(void* context) { static_cast<TestUart*>(context)->AddToLog("stopHw"); }
    static void startHw(void* context) { static_cast<TestUart*>(context)->AddToLog("startHw"); }
    static bool ConfigOk(const void* context) { return static_cast<const TestUart*>(context)->configOk; }

    void AddToLog(const std::string& l)
    {
      if (!log.empty()) { log += ':'; }
      log += l;
    }

    std::string log;
  };

  TEST_F(TestUart, InitialState)
  {
    EXPECT_EQ("IDLE", CurrentStateName());
    EXPECT_EQ("", Log());
  }

  TEST_F(TestUart, SaveConfig)
  {
    SmUart_configure(&smUart);
    EXPECT_EQ("saveConfig", Log());
    EXPECT_EQ("IDLE", CurrentStateName());
  }

  TEST_F(TestUart, SetError)
  {
    configOk = false;
    SmUart_start(&smUart);
    EXPECT_EQ("setError", Log());
    EXPECT_EQ("IDLE", CurrentStateName());
  }

  TEST_F(TestUart, ConfigureHw)
  {
    configOk = true;
    SmUart_start(&smUart);
    EXPECT_EQ("configureHw", Log());
    EXPECT_EQ("RUNNING", CurrentStateName());
  }

  TEST_F(TestUart, SuspendResume)
  {
    configOk = true;
    SmUart_start(&smUart);
    SmUart_suspend(&smUart);
    SmUart_stopped(&smUart);
    SmUart_resume(&smUart);
    EXPECT_EQ("configureHw:stopHw:startHw", Log());
    EXPECT_EQ("RUNNING", CurrentStateName());
  }

  TEST_F(TestUart, SuspendStop)
  {
    configOk = true;
    SmUart_start(&smUart);
    SmUart_suspend(&smUart);
    SmUart_stopped(&smUart);
    SmUart_stop(&smUart);
    EXPECT_EQ("configureHw:stopHw", Log());
    EXPECT_EQ("IDLE", CurrentStateName());
  }

  TEST_F(TestUart, StartStop)
  {
    configOk = true;
    SmUart_start(&smUart);
    SmUart_stop(&smUart);
    SmUart_stopped(&smUart);
    EXPECT_EQ("configureHw:stopHw", Log());
    EXPECT_EQ("IDLE", CurrentStateName());
  }
}