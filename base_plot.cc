#include "base_plot.h"

#include <set>
#include <string>
#include <vector>

#include "python_random.h"
#include "transplot_db.h"

namespace transplot {

const std::vector<Rgb>& BasePlot::PredefinedColors() {
  static const std::vector<Rgb> kColors = {
      {0, 0, 255},      // Blue
      {255, 0, 0},      // Red
      {0, 128, 0},      // Green
      {165, 42, 42},    // Brown
      {238, 130, 238},  // Violet
      {255, 255, 0},    // Yellow
      {0, 0, 0},        // Black
      {128, 128, 0},    // Olive
      {255, 255, 240},  // Ivory
      {255, 165, 0},    // Orange
      {255, 192, 203},  // Pink
      {0, 255, 255},    // Aqua
      {210, 105, 30},   // Chocolate
      {30, 144, 255},   // DodgerBlue
      {0, 255, 0},      // Lime
      {100, 149, 237},  // CornflowerBlue
      {75, 0, 130},     // Indigo
      {128, 0, 128},    // Purple
      {210, 180, 140},  // Tan
      {46, 139, 87},    // SeaGreen
  };
  return kColors;
}

void BasePlot::SetTargetSdc(const std::vector<std::string>& sdc) {
  target_sdc_ = std::set<std::string>(sdc.begin(), sdc.end());
}

void BasePlot::SetTargetTransistors(
    const std::vector<std::string>& transistors) {
  target_transistors_ =
      std::set<std::string>(transistors.begin(), transistors.end());
}

void BasePlot::BuildColorMap() {
  colors_ = PredefinedColors();

  // Sorted (as strings) list of SDC groups with more than 2 transistors.
  // data_.sdc_group is a btree_map, so iteration is already lexicographically
  // sorted, matching Python's sorted(keys, key=str).
  std::vector<std::string> keys;
  for (const auto& [sdc, count] : data_.sdc_group) {
    if (count > 2) keys.push_back(sdc);
  }

  // Generate extra colors if there are more groups than predefined colors,
  // using the CPython-compatible RNG seeded with 0 (matches _generate_colors).
  const int num_groups = static_cast<int>(keys.size());
  const int num_predefined = static_cast<int>(colors_.size());
  if (num_groups > num_predefined) {
    PythonRandom rng;  // Constructor seeds with 0.
    for (int i = 0; i < num_groups - num_predefined; i++) {
      Rgb c;
      c.r = rng.RandInt(0, 255);
      c.g = rng.RandInt(0, 255);
      c.b = rng.RandInt(0, 255);
      colors_.push_back(c);
    }
  }

  color_map_.clear();
  for (std::size_t i = 0; i < keys.size(); i++) {
    color_map_[keys[i]] = colors_[i];
  }
}

bool BasePlot::IsTransistorToColorPlot(const Transistor& t) const {
  auto it = data_.sdc_group.find(t.sdc);
  if (it == data_.sdc_group.end() || it->second <= 2) return false;
  if (target_sdc_.has_value()) {
    return target_sdc_->count(t.sdc) > 0;
  }
  if (target_transistors_.has_value()) {
    return target_transistors_->count(t.name) > 0;
  }
  return true;
}

const Rgb& BasePlot::ColorForSdc(const std::string& sdc) const {
  return color_map_.at(sdc);
}

}  // namespace transplot
