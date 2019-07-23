#include <gtest/gtest.h>
#include "CompositeState.hpp"
#include <functional>

class CompositeStateTest : public ::testing::Test
{
protected:
    compositestate::StateMachine sm;
};

TEST_F(CompositeStateTest, InitialState)
{
    EXPECT_EQ(compositestate::StateId_S1, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1", sm.Log());
}

TEST_F(CompositeStateTest, Event0)
{
    sm.E0();
    EXPECT_EQ(compositestate::StateId_S2, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A0:EntryS2", sm.Log());
}

TEST_F(CompositeStateTest, Event1)
{
    sm.E0();
    sm.E1();
    EXPECT_EQ(compositestate::StateId_S1, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A0:EntryS2:ExitS2:A1:EntryS1", sm.Log());
}

TEST_F(CompositeStateTest, Event2)
{
    sm.E2();
    EXPECT_EQ(compositestate::StateId_S3, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3", sm.Log());
}

TEST_F(CompositeStateTest, Event3)
{
    sm.E2();
    sm.E3();
    EXPECT_EQ(compositestate::StateId_S1, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:ExitS3:A3", sm.Log());
}

TEST_F(CompositeStateTest, Event0InS3)
{
    sm.E2();
    sm.E0();
    EXPECT_EQ(compositestate::StateId_S2, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:ExitS3:ExitS1:A0:EntryS2", sm.Log());
}

TEST_F(CompositeStateTest, Event6_TransitionToSelfOnCompositeState)
{
    sm.E6();
    EXPECT_EQ(compositestate::StateId_S1, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A6:EntryS1", sm.Log());
}

TEST_F(CompositeStateTest, Event7_TransitionToSelfOnLeafState)
{
    sm.E0();
    sm.E7();
    EXPECT_EQ(compositestate::StateId_S2, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:ExitS1:A0:EntryS2:ExitS2:A7:EntryS2", sm.Log());
}

TEST_F(CompositeStateTest, Event4InS1)
{
    sm.E4();
    EXPECT_EQ(compositestate::StateId_S1, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A4", sm.Log());
}

TEST_F(CompositeStateTest, Event4InS3)
{
    sm.E2();
    sm.E4();
    EXPECT_EQ(compositestate::StateId_S3, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:A4", sm.Log());
}

TEST_F(CompositeStateTest, Event8InS1)
{
    sm.E8();
    EXPECT_EQ(compositestate::StateId_S1, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A8", sm.Log());
}

TEST_F(CompositeStateTest, Event8InS3)
{
    sm.E2();
    sm.E8();
    EXPECT_EQ(compositestate::StateId_S3, sm.CurrentState());
    EXPECT_EQ("EntryS0:EntryS1:A2:EntryS3:A9", sm.Log());
}