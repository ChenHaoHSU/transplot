// Renders TransplotData to a PNG using the Cairo C library, reproducing
// cairo_plot.py (CairoPlot) exactly: a fixed 2000x2000 ARGB surface, white
// background, y-flip, min-scale fit with a 2000-unit margin, and the same draw
// order (rows -> ports -> transistors -> pins -> sdcs -> paths).

#ifndef TRANSPLOT_CAIRO_PLOT_H_
#define TRANSPLOT_CAIRO_PLOT_H_

#include <string>

#include "base_plot.h"
#include "transplot_db.h"

namespace transplot {

class CairoPlot : public BasePlot {
 public:
  static constexpr const char* kDefaultPngName = "cairo_plot.png";

  explicit CairoPlot(const TransplotData& data) : BasePlot(data) {}

  // Renders to `png_name` (or kDefaultPngName if empty). Returns true on
  // success.
  bool Plot(const std::string& png_name);
};

}  // namespace transplot

#endif  // TRANSPLOT_CAIRO_PLOT_H_
