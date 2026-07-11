// Data structures shared by the transplot reader and plotter.
//
// Mirrors the unified `data` dictionary produced by the Python readers in
// reader.py. Fields use std::optional to distinguish "not present in the input"
// from a legitimate zero value (matching Python's `None` defaults).

#ifndef TRANSPLOT_TRANSPLOT_DB_H_
#define TRANSPLOT_TRANSPLOT_DB_H_

#include <array>
#include <optional>
#include <string>
#include <utility>
#include <vector>

#include "absl/container/btree_map.h"

namespace transplot {

// A single transistor placement record.
struct Transistor {
  std::string name;
  int x = 0;
  int y = 0;
  int flipped = 0;
  std::string type;  // "PMOS" or "NMOS".
  std::string sdc;   // SDC group id, kept as a string (matches Python).
};

// A rectangular I/O port.
struct Port {
  std::string name;
  std::string net_name;
  int x = 0;
  int y = 0;
  int width = 0;
  int height = 0;
};

// A point pin.
struct Pin {
  std::string name;
  std::string net_name;
  int x = 0;
  int y = 0;
};

// A bounding rectangle for an SDC/macro region.
struct Sdc {
  std::string name;
  std::string macro;
  int x = 0;
  int y = 0;
  int width = 0;
  int height = 0;
};

// A single routing edge: ((x1, y1), (x2, y2)).
struct Edge {
  int x1 = 0;
  int y1 = 0;
  int x2 = 0;
  int y2 = 0;
};

// A routing path is an ordered list of edges.
using Path = std::vector<Edge>;

// The unified parsed data, matching the Python `data` dict keys.
struct TransplotData {
  std::optional<int> units;
  std::optional<std::array<int, 4>> die_area;  // (xl, yl, xh, yh)
  std::optional<int> row_height;
  std::optional<int> site_width;
  std::optional<int> num_rows;
  std::optional<int> num_sites;
  std::optional<int> transistor_offset;

  std::vector<Port> ports;
  std::vector<Transistor> transistors;
  std::vector<Pin> pins;
  std::vector<Sdc> sdcs;
  std::vector<Path> paths;

  // SDC group -> transistor count. btree_map keeps keys ordered, but the color
  // map sorts keys lexicographically (as strings) itself, so ordering here is
  // only for deterministic iteration.
  absl::btree_map<std::string, int> sdc_group;
};

}  // namespace transplot

#endif  // TRANSPLOT_TRANSPLOT_DB_H_
