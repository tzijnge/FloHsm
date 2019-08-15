#include "gtest/gtest.h"
#include "Hsm/Alignment.hpp"


class AlignmentTest : public testing::Test
{
};

struct Test123
{
    uint8_t a;
    uint64_t b;
    uint8_t c;
    bool d;
};

TEST_F(AlignmentTest, MaxSizeForTypes)
{
    auto m = MaxSizeForTypes<uint8_t, uint8_t>::value;
    EXPECT_EQ(static_cast<size_t>(1), m);

    m = MaxSizeForTypes<uint8_t, uint64_t>::value;
    EXPECT_EQ(static_cast<size_t>(8), m);

    m = MaxSizeForTypes<uint64_t, uint8_t>::value;
    EXPECT_EQ(static_cast<size_t>(8), m);

    m = MaxSizeForTypes<uint64_t, uint8_t, Test123>::value;
    EXPECT_EQ(static_cast<size_t>(24), m);
}