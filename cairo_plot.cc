#include "cairo_plot.h"

#include <cairo.h>

#include <array>
#include <cstdio>
#include <string>

#include "base_plot.h"
#include "transplot_db.h"

namespace transplot {
namespace {

struct Rgba {
  double r = 0;
  double g = 0;
  double b = 0;
  double a = 1;
};

Rgba ToFloatRgb(const Rgb& c, double alpha) {
  return Rgba{c.r / 255.0, c.g / 255.0, c.b / 255.0, alpha};
}

// Fixed rendering parameters, matching CairoPlot.params in cairo_plot.py. The
// linewidths are the *unadjusted* base values; they are divided by the scale
// factor before drawing.
constexpr double kRowLinewidthBase = 1.0;
constexpr double kTransistorLinewidthBase = 0.5;
constexpr double kSdcLinewidthBase = 5.0;
constexpr double kPathLinewidth = 8.0;  // Not scale-adjusted.

// Colors passed "raw" to cairo (clamped by cairo to [0,1]) in the Python code.
constexpr Rgba kRowStroke = {0, 0, 0, 1};
constexpr Rgba kPortFill = {255, 0, 0, 0.5};
constexpr Rgba kPinFill = {0, 0, 0, 1.0};
constexpr Rgba kSdcStroke = {0, 0, 0, 1};
constexpr Rgba kPathStroke = {0.0, 0.0, 0.0, 1.0};

// Colors converted via /255 in the Python code.
const Rgb kTransistorFillGray = {8, 8, 8};
const Rgb kTransistorStroke = {0, 0, 0};
const Rgb kSdcFill = {8, 8, 8};  // alpha 0.4 applied separately.

constexpr double kTransistorStrokeAlpha = 1.0;
constexpr double kTransistorPolyShrink = 0.2;
constexpr double kTransistorDiffusionShrink = 0.5;
constexpr int kPlotMargin = 2000;
constexpr double kPinSizeRatio = 0.1;
constexpr double kSdcFillAlpha = 0.4;

double TransistorAlpha(const std::string& type) {
  return type == "PMOS" ? 0.9 : 0.5;  // NMOS -> 0.5
}
double TransistorAlphaInv(const std::string& type) {
  return type == "PMOS" ? 0.25 : 0.4;  // NMOS -> 0.4
}

void SetSource(cairo_t* cr, const Rgba& c) {
  cairo_set_source_rgba(cr, c.r, c.g, c.b, c.a);
}

// Draws a rectangle mirroring CairoRect.draw() exactly (including the redundant
// second rectangle path when both fill and stroke are enabled).
void DrawRect(cairo_t* cr, double x, double y, double w, double h, bool fill,
              const Rgba& fill_rgba, bool stroke, const Rgba& stroke_rgba,
              double linewidth) {
  if (fill) {
    SetSource(cr, fill_rgba);
    cairo_rectangle(cr, x, y, w, h);
    if (stroke) {
      cairo_fill_preserve(cr);
    } else {
      cairo_fill(cr);
    }
  }
  if (stroke) {
    SetSource(cr, stroke_rgba);
    cairo_set_line_width(cr, linewidth);
    cairo_rectangle(cr, x, y, w, h);
    cairo_stroke(cr);
  }
}

}  // namespace

bool CairoPlot::Plot(const std::string& png_name_in) {
  std::string png_name = png_name_in.empty() ? kDefaultPngName : png_name_in;

  const int surface_width = 2000;
  const int surface_height = 2000;
  cairo_surface_t* surface = cairo_image_surface_create(
      CAIRO_FORMAT_ARGB32, surface_width, surface_height);
  cairo_t* cr = cairo_create(surface);

  // White background.
  cairo_set_source_rgb(cr, 1, 1, 1);
  cairo_paint(cr);

  // Move origin to bottom-left and flip the y-axis.
  cairo_translate(cr, 0, surface_height);
  cairo_scale(cr, 1, -1);

  // Die area and plot boundary (+/- margin).
  std::array<int, 4> die = data_.die_area.value_or(std::array<int, 4>{0, 0, 0, 0});
  const int die_xl = die[0], die_yl = die[1], die_xh = die[2], die_yh = die[3];
  const int die_width = die_xh - die_xl;
  const int die_height = die_yh - die_yl;

  int x_low = 0, y_low = 0, x_high = 0, y_high = 0;
  if (data_.die_area.has_value()) {
    x_low = die_xl - kPlotMargin;
    y_low = die_yl - kPlotMargin;
    x_high = die_xh + kPlotMargin;
    y_high = die_yh + kPlotMargin;
  }
  const int actual_width = x_high - x_low;
  const int actual_height = y_high - y_low;

  const double scale_x = static_cast<double>(surface_width) / actual_width;
  const double scale_y = static_cast<double>(surface_height) / actual_height;
  const double scale_factor = scale_x < scale_y ? scale_x : scale_y;
  cairo_scale(cr, scale_factor, scale_factor);

  cairo_translate(cr, (surface_width / scale_factor - die_width) / 2.0,
                  (surface_height / scale_factor - die_height) / 2.0);

  // Adjust linewidths by the scale factor (done before building shapes in the
  // Python code; here we just precompute the adjusted values).
  const double row_lw = kRowLinewidthBase / scale_factor;
  const double transistor_lw = kTransistorLinewidthBase / scale_factor;
  const double sdc_lw = kSdcLinewidthBase / scale_factor;

  // --- Rows ---
  if (data_.num_rows.value_or(0) != 0 && data_.die_area.has_value() &&
      data_.row_height.value_or(0) != 0) {
    const int row_width = die_xh - die_xl;
    const int row_height = *data_.row_height;
    for (int i = 0; i < *data_.num_rows; i++) {
      DrawRect(cr, die_xl, die_yl + i * row_height, row_width, row_height,
               /*fill=*/false, Rgba{}, /*stroke=*/true, kRowStroke, row_lw);
    }
  }

  // --- Ports ---
  if (data_.ports.empty()) {
    printf("[CairoPlot] Warning: ports not found.\n");
  }
  for (const Port& p : data_.ports) {
    DrawRect(cr, p.x, p.y, p.width, p.height, /*fill=*/true, kPortFill,
             /*stroke=*/false, Rgba{}, 0);
  }

  // --- Transistors ---
  if (data_.transistors.empty()) {
    printf("[CairoPlot] Warning: transistors not found.\n");
  } else if (data_.site_width.value_or(0) == 0) {
    printf("[CairoPlot] Warning: site width not found.\n");
  } else if (data_.row_height.value_or(0) == 0) {
    printf("[CairoPlot] Warning: row height not found.\n");
  } else {
    const int half_site_width = *data_.site_width / 2;  // floor division
    const int tran_width = *data_.site_width;
    const double tran_height = *data_.row_height / 2.0;
    const Rgba stroke_rgba = ToFloatRgb(kTransistorStroke, kTransistorStrokeAlpha);

    const double diff_y_offset =
        tran_height * (1 - kTransistorDiffusionShrink) / 2;
    const double diff_height = tran_height * kTransistorDiffusionShrink;
    const double poly_x_offset = tran_width * (1 - kTransistorPolyShrink) / 2;
    const double poly_width = tran_width * kTransistorPolyShrink;

    const bool has_offset = data_.transistor_offset.value_or(0) != 0;
    const int offset = data_.transistor_offset.value_or(0);

    for (const Transistor& t : data_.transistors) {
      Rgba fill_rgba;
      if (IsTransistorToColorPlot(t)) {
        fill_rgba = ToFloatRgb(ColorForSdc(t.sdc), TransistorAlpha(t.type));
      } else {
        fill_rgba = ToFloatRgb(kTransistorFillGray, TransistorAlphaInv(t.type));
      }

      int tran_x = t.x + half_site_width;
      if (has_offset) tran_x += offset;
      const int tran_y = t.y;

      // Diffusion rectangle.
      DrawRect(cr, tran_x, tran_y + diff_y_offset, tran_width, diff_height,
               /*fill=*/true, fill_rgba, /*stroke=*/true, stroke_rgba,
               transistor_lw);
      // Poly rectangle.
      DrawRect(cr, tran_x + poly_x_offset, tran_y, poly_width, tran_height,
               /*fill=*/true, fill_rgba, /*stroke=*/true, stroke_rgba,
               transistor_lw);
    }
  }

  // --- Pins ---
  if (data_.pins.empty()) {
    printf("[CairoPlot] Warning: pins not found.\n");
  } else {
    const double pin_w = kPinSizeRatio * data_.row_height.value_or(0);
    const double pin_h = kPinSizeRatio * data_.row_height.value_or(0);
    const double pin_hw = pin_w / 2, pin_hh = pin_h / 2;
    const bool has_offset = data_.transistor_offset.value_or(0) != 0;
    const int offset = data_.transistor_offset.value_or(0);
    for (const Pin& p : data_.pins) {
      int pin_x = p.x;
      if (has_offset) pin_x += offset;
      const int pin_y = p.y;
      DrawRect(cr, pin_x - pin_hw, pin_y - pin_hh, pin_w, pin_h,
               /*fill=*/true, kPinFill, /*stroke=*/false, Rgba{}, 0);
    }
  }

  // --- SDCs ---
  if (data_.sdcs.empty()) {
    printf("[CairoPlot] Warning: sdcs not found.\n");
  } else {
    const Rgba sdc_fill = ToFloatRgb(kSdcFill, kSdcFillAlpha);
    for (const Sdc& s : data_.sdcs) {
      DrawRect(cr, s.x, s.y, s.width, s.height, /*fill=*/true, sdc_fill,
               /*stroke=*/true, kSdcStroke, sdc_lw);
    }
  }

  // --- Paths ---
  if (data_.paths.empty()) {
    printf("[CairoPlot] Warning: paths not found.\n");
  } else {
    for (const Path& path : data_.paths) {
      SetSource(cr, kPathStroke);
      cairo_set_line_width(cr, kPathLinewidth);
      for (const Edge& e : path) {
        cairo_move_to(cr, e.x1, e.y1);
        cairo_line_to(cr, e.x2, e.y2);
      }
      cairo_stroke(cr);
    }
  }

  cairo_status_t status = cairo_surface_write_to_png(surface, png_name.c_str());

  cairo_destroy(cr);
  cairo_surface_destroy(surface);

  if (status != CAIRO_STATUS_SUCCESS) {
    fprintf(stderr, "[CairoPlot] Error writing PNG: %s\n",
            cairo_status_to_string(status));
    return false;
  }
  printf("[CairoPlot] Image saved to '%s'.\n", png_name.c_str());
  return true;
}

}  // namespace transplot
