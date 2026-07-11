#include "reader.h"

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>

#include "gtest/gtest.h"
#include "transplot_db.h"

namespace transplot {
namespace {

// Writes `content` to a unique temp file and returns its path.
std::string WriteTemp(const std::string& content, const std::string& suffix) {
  const char* dir = std::getenv("TEST_TMPDIR");
  std::string path =
      std::string(dir ? dir : "/tmp") + "/tp_" + suffix;
  std::ofstream out(path, std::ios::binary);
  out << content;
  out.close();
  return path;
}

TEST(ReaderTest, V1BlockForm) {
  const std::string tp =
      "UNITS 8000\n"
      "DIEAREA 0 0 100 200\n"
      "ROWHEIGHT 10\n"
      "SITEWIDTH 5\n"
      "ROWS 2\n"
      "SITES 20\n"
      "TRANSISTORS 3\n"
      "A 1 2 0 PMOS 0\n"
      "B 3 4 0 NMOS 0\n"
      "C 5 6 0 PMOS 1\n"
      "END TRANSISTORS\n";
  const std::string path = WriteTemp(tp, "v1.tp");
  TransplotData data;
  ASSERT_TRUE(ReadV1(path, &data));
  EXPECT_EQ(data.units.value_or(-1), 8000);
  ASSERT_TRUE(data.die_area.has_value());
  EXPECT_EQ((*data.die_area)[2], 100);
  EXPECT_EQ(data.transistors.size(), 3u);
  EXPECT_EQ(data.transistors[0].name, "A");
  EXPECT_EQ(data.transistors[2].sdc, "1");
  EXPECT_EQ(data.sdc_group.at("0"), 2);
  EXPECT_EQ(data.sdc_group.at("1"), 1);
}

TEST(ReaderTest, V1RejectsKeywordTransistor) {
  // A singular-keyword TRANSISTOR line is NOT valid V1 (matches Python: V1 only
  // handles the block form, so example1-style files fall through to V2).
  const std::string tp =
      "UNITS 8000\n"
      "TRANSISTOR A 1 2 0 PMOS 0\n";
  const std::string path = WriteTemp(tp, "v1bad.tp");
  TransplotData data;
  EXPECT_FALSE(ReadV1(path, &data));
}

TEST(ReaderTest, V2KeywordForm) {
  const std::string tp =
      "UNITS 8000\n"
      "DIEAREA 0 0 100 200\n"
      "ROWHEIGHT 10\n"
      "SITEWIDTH 5\n"
      "ROWS 2\n"
      "SITES 20\n"
      "PORT p0 net0 1 2 3 4\n"
      "TRANSISTOR A 1 2 0 PMOS 0\n"
      "TRANSISTOR B 3 4 0 NMOS 0\n"
      "PIN pin0 7 8 net1\n"
      "SDC s0 macro0 0 0 50 50\n"
      "PATH ( 1 2 3 4 ) ( 5 6 7 8 )\n";
  const std::string path = WriteTemp(tp, "v2.tp");
  TransplotData data;
  ASSERT_TRUE(ReadV2(path, &data));
  EXPECT_EQ(data.ports.size(), 1u);
  EXPECT_EQ(data.transistors.size(), 2u);
  EXPECT_EQ(data.pins.size(), 1u);
  EXPECT_EQ(data.sdcs.size(), 1u);
  ASSERT_EQ(data.paths.size(), 1u);
  ASSERT_EQ(data.paths[0].size(), 2u);
  EXPECT_EQ(data.paths[0][0].x1, 1);
  EXPECT_EQ(data.paths[0][1].y2, 8);
  EXPECT_EQ(data.pins[0].net_name, "net1");
}

TEST(ReaderTest, V2TransistorOffsetNotConfusedWithTransistor) {
  const std::string tp =
      "TRANSISTOROFFSET 500\n"
      "TRANSISTOR A 1 2 0 PMOS 0\n";
  const std::string path = WriteTemp(tp, "v2off.tp");
  TransplotData data;
  ASSERT_TRUE(ReadV2(path, &data));
  EXPECT_EQ(data.transistor_offset.value_or(-1), 500);
  EXPECT_EQ(data.transistors.size(), 1u);
}

TEST(ReaderTest, JsonForm) {
  const std::string tp = R"({
    "canvas": {"die_area": {"xl": 0, "yl": 0, "xh": 100, "yh": 200},
               "row_height": 10, "site_width": 5, "rows": 2, "sites": 20},
    "transistors": [
      {"name": "A", "x": 1, "y": 2, "type": "PMOS", "sdc": "0"},
      {"name": "B", "x": 3, "y": 4, "type": "NMOS", "sdc": "0"}
    ],
    "paths": [{"edges": [{"from_node": {"x": 1, "y": 2},
                          "to_node": {"x": 3, "y": 4}}]}]
  })";
  const std::string path = WriteTemp(tp, "j.tp");
  TransplotData data;
  ASSERT_TRUE(ReadJson(path, &data));
  EXPECT_EQ(data.transistors.size(), 2u);
  EXPECT_EQ(data.num_sites.value_or(-1), 20);
  ASSERT_EQ(data.paths.size(), 1u);
  EXPECT_EQ(data.paths[0][0].x2, 3);
}

TEST(ReaderTest, AutoDetectPrefersV2ForKeywordFile) {
  const std::string tp =
      "DIEAREA 0 0 100 200\n"
      "TRANSISTOR A 1 2 0 PMOS 0\n";
  const std::string path = WriteTemp(tp, "auto.tp");
  TransplotData data;
  ASSERT_TRUE(ReadTransplot(path, &data));
  EXPECT_EQ(data.transistors.size(), 1u);
}

}  // namespace
}  // namespace transplot
