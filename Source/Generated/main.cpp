#include "gtest/gtest.h"

void main(int argc, char **argv)
{
    testing::FLAGS_gtest_repeat = 1;
    //testing::FLAGS_gtest_filter = "*ActionWithArgumentTest*";

    ::testing::InitGoogleTest(&argc, argv);
    RUN_ALL_TESTS();
}