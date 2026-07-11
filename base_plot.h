// Shared plot logic (color assignment + target filtering), mirroring
// base_plot.py's BasePlot. Rendering is left to CairoPlot.

#ifndef TRANSPLOT_BASE_PLOT_H_
#define TRANSPLOT_BASE_PLOT_H_

#include <array>
#include <optional>
#include <set>
#include <string>
#include <vector>

#include "absl/container/flat_hash_map.h"
#include "transplot_db.h"

namespace transplot {

// An 8-bit RGB color.
struct Rgb {
  int r = 0;
  int g = 0;
  int b = 0;
};

class BasePlot {
 public:
  // The 20 predefined colors from base_plot.py, in order.
  static const std::vector<Rgb>& PredefinedColors();

  explicit BasePlot(const TransplotData& data) : data_(data) {
    BuildColorMap();
  }
  virtual ~BasePlot() = default;

  // Sets the target SDCs / transistors (from the -s / -t CLI flags).
  void SetTargetSdc(const std::vector<std::string>& sdc);
  void SetTargetTransistors(const std::vector<std::string>& transistors);

  // Whether a transistor should be drawn in color (vs. gray "inverter" fill).
  bool IsTransistorToColorPlot(const Transistor& t) const;

  // The color assigned to an SDC group (only valid for groups with >2 members).
  const Rgb& ColorForSdc(const std::string& sdc) const;

 protected:
  const TransplotData& data_;

 private:
  void BuildColorMap();

  std::vector<Rgb> colors_;
  absl::flat_hash_map<std::string, Rgb> color_map_;
  std::optional<std::set<std::string>> target_sdc_;
  std::optional<std::set<std::string>> target_transistors_;
};

}  // namespace transplot

#endif  // TRANSPLOT_BASE_PLOT_H_
