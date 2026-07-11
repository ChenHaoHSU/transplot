#include "python_random.h"

#include <vector>

#include "gtest/gtest.h"

namespace transplot {
namespace {

// Golden vectors captured from CPython 3.11 after random.seed(0).
TEST(PythonRandomTest, RandIntMatchesCPython) {
  PythonRandom rng;  // seeds 0
  const std::vector<int> expected = {197, 215, 20,  132, 248, 207, 155, 244,
                                     183, 111, 71,  144, 71,  48,  128, 75,
                                     158, 50,  37,  169, 241, 51,  181, 222,
                                     161, 104, 244, 226, 133, 31};
  for (int e : expected) {
    EXPECT_EQ(rng.RandInt(0, 255), e);
  }
}

TEST(PythonRandomTest, GetRandBits9MatchesCPython) {
  PythonRandom rng;
  const std::vector<uint32_t> expected = {432, 197, 388, 455, 215, 20, 132, 494,
                                          261, 248, 207, 470, 401, 424, 155};
  for (uint32_t e : expected) {
    EXPECT_EQ(rng.GetRandBits(9), e);
  }
}

TEST(PythonRandomTest, RandomColorTriplesMatchCPython) {
  PythonRandom rng;
  const int expected[5][3] = {{197, 215, 20},
                              {132, 248, 207},
                              {155, 244, 183},
                              {111, 71, 144},
                              {71, 48, 128}};
  for (const auto& t : expected) {
    EXPECT_EQ(rng.RandInt(0, 255), t[0]);
    EXPECT_EQ(rng.RandInt(0, 255), t[1]);
    EXPECT_EQ(rng.RandInt(0, 255), t[2]);
  }
}

}  // namespace
}  // namespace transplot
