#include "reader.h"

#include <array>
#include <charconv>
#include <fstream>
#include <regex>
#include <sstream>
#include <string>
#include <vector>

#include "nlohmann/json.hpp"
#include "transplot_db.h"

namespace transplot {
namespace {

// Splits on runs of ASCII whitespace, discarding empties (Python str.split()).
std::vector<std::string> Split(const std::string& line) {
  std::vector<std::string> tokens;
  std::size_t i = 0;
  const std::size_t n = line.size();
  while (i < n) {
    while (i < n && std::isspace(static_cast<unsigned char>(line[i]))) i++;
    std::size_t start = i;
    while (i < n && !std::isspace(static_cast<unsigned char>(line[i]))) i++;
    if (i > start) tokens.push_back(line.substr(start, i - start));
  }
  return tokens;
}

// Parses a full token as a base-10 integer, like Python's int(). Requires the
// entire token to be consumed (rejects trailing garbage). Accepts a leading
// '+'/'-'. Throws-equivalent is signaled via the bool return.
bool ParseInt(const std::string& tok, int* out) {
  if (tok.empty()) return false;
  const char* begin = tok.data();
  const char* end = tok.data() + tok.size();
  // std::from_chars handles an optional leading '-' but not '+'.
  if (tok[0] == '+') begin++;
  int value = 0;
  auto [ptr, ec] = std::from_chars(begin, end, value);
  if (ec != std::errc() || ptr != end) return false;
  *out = value;
  return true;
}

bool StartsWith(const std::string& s, const char* prefix) {
  return s.rfind(prefix, 0) == 0;
}

// Reads all lines of a file the way Python's file.read().splitlines() does:
// splits on \n, dropping a single trailing newline (no trailing empty line).
bool ReadLines(const std::string& path, std::vector<std::string>* lines) {
  std::ifstream in(path, std::ios::binary);
  if (!in) return false;
  std::stringstream ss;
  ss << in.rdbuf();
  std::string content = ss.str();
  std::string cur;
  for (char c : content) {
    if (c == '\n') {
      // Strip a trailing '\r' for CRLF files (splitlines drops it too).
      if (!cur.empty() && cur.back() == '\r') cur.pop_back();
      lines->push_back(cur);
      cur.clear();
    } else {
      cur.push_back(c);
    }
  }
  if (!cur.empty()) {
    if (cur.back() == '\r') cur.pop_back();
    lines->push_back(cur);
  }
  return true;
}

bool ParseDieArea(const std::vector<std::string>& tokens,
                  std::array<int, 4>* out) {
  // tokens[0] is the keyword; expect exactly 4 values after it.
  if (tokens.size() != 5) return false;
  for (int i = 0; i < 4; i++) {
    if (!ParseInt(tokens[i + 1], &(*out)[i])) return false;
  }
  return true;
}

// KEY VALUE -> int, requiring exactly 2 tokens (Python _parse_int).
bool ParseKeyInt(const std::vector<std::string>& tokens, int* out) {
  if (tokens.size() != 2) return false;
  return ParseInt(tokens[1], out);
}

}  // namespace

bool ReadV1(const std::string& path, TransplotData* data) {
  std::vector<std::string> lines;
  if (!ReadLines(path, &lines)) return false;

  *data = TransplotData{};
  bool parsing_transistors = false;
  int num_transistors = 0;

  for (const std::string& line : lines) {
    if (parsing_transistors) {
      if (static_cast<int>(data->transistors.size()) >= num_transistors) {
        if (StartsWith(line, "END TRANSISTORS")) {
          parsing_transistors = false;
          continue;
        }
        return false;  // Expected END TRANSISTORS.
      }
      // Bare transistor record: name x y flipped type sdc (6 tokens).
      std::vector<std::string> t = Split(line);
      if (t.size() != 6) return false;
      Transistor tr;
      tr.name = t[0];
      if (!ParseInt(t[1], &tr.x)) return false;
      if (!ParseInt(t[2], &tr.y)) return false;
      if (!ParseInt(t[3], &tr.flipped)) return false;
      tr.type = t[4];
      tr.sdc = t[5];
      data->sdc_group[tr.sdc]++;
      data->transistors.push_back(std::move(tr));
      continue;
    }

    std::vector<std::string> tokens = Split(line);
    if (StartsWith(line, "UNITS")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      data->units = v;
    } else if (StartsWith(line, "DIEAREA")) {
      std::array<int, 4> da;
      if (!ParseDieArea(tokens, &da)) return false;
      data->die_area = da;
    } else if (StartsWith(line, "ROWHEIGHT")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      data->row_height = v;
    } else if (StartsWith(line, "SITEWIDTH")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      data->site_width = v;
    } else if (StartsWith(line, "ROWS")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      data->num_rows = v;
    } else if (StartsWith(line, "SITES")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      data->num_sites = v;
    } else if (StartsWith(line, "TRANSISTOROFFSET")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      data->transistor_offset = v;
    } else if (StartsWith(line, "TRANSISTORS")) {
      int v;
      if (!ParseKeyInt(tokens, &v)) return false;
      parsing_transistors = true;
      num_transistors = v;
    } else {
      return false;  // Unknown line.
    }
  }
  return true;
}

bool ReadV2(const std::string& path, TransplotData* data) {
  std::vector<std::string> lines;
  if (!ReadLines(path, &lines)) return false;

  *data = TransplotData{};

  for (const std::string& line : lines) {
    std::vector<std::string> t = Split(line);
    if (StartsWith(line, "UNITS")) {
      int v;
      if (!ParseKeyInt(t, &v)) return false;
      data->units = v;
    } else if (StartsWith(line, "DIEAREA")) {
      std::array<int, 4> da;
      if (!ParseDieArea(t, &da)) return false;
      data->die_area = da;
    } else if (StartsWith(line, "ROWHEIGHT")) {
      int v;
      if (!ParseKeyInt(t, &v)) return false;
      data->row_height = v;
    } else if (StartsWith(line, "SITEWIDTH")) {
      int v;
      if (!ParseKeyInt(t, &v)) return false;
      data->site_width = v;
    } else if (StartsWith(line, "ROWS")) {
      int v;
      if (!ParseKeyInt(t, &v)) return false;
      data->num_rows = v;
    } else if (StartsWith(line, "SITES")) {
      int v;
      if (!ParseKeyInt(t, &v)) return false;
      data->num_sites = v;
    } else if (StartsWith(line, "PORT")) {
      if (t.size() != 7) return false;
      Port p;
      p.name = t[1];
      p.net_name = t[2];
      if (!ParseInt(t[3], &p.x)) return false;
      if (!ParseInt(t[4], &p.y)) return false;
      if (!ParseInt(t[5], &p.width)) return false;
      if (!ParseInt(t[6], &p.height)) return false;
      data->ports.push_back(std::move(p));
    } else if (StartsWith(line, "TRANSISTOROFFSET")) {
      int v;
      if (!ParseKeyInt(t, &v)) return false;
      data->transistor_offset = v;
    } else if (StartsWith(line, "TRANSISTOR")) {
      if (t.size() != 7) return false;
      Transistor tr;
      tr.name = t[1];
      if (!ParseInt(t[2], &tr.x)) return false;
      if (!ParseInt(t[3], &tr.y)) return false;
      if (!ParseInt(t[4], &tr.flipped)) return false;
      tr.type = t[5];
      tr.sdc = t[6];
      data->sdc_group[tr.sdc]++;
      data->transistors.push_back(std::move(tr));
    } else if (StartsWith(line, "PIN")) {
      if (t.size() != 5) return false;
      Pin p;
      p.name = t[1];
      if (!ParseInt(t[2], &p.x)) return false;
      if (!ParseInt(t[3], &p.y)) return false;
      p.net_name = t[4];
      data->pins.push_back(std::move(p));
    } else if (StartsWith(line, "SDC")) {
      if (t.size() != 7) return false;
      Sdc s;
      s.name = t[1];
      s.macro = t[2];
      if (!ParseInt(t[3], &s.x)) return false;
      if (!ParseInt(t[4], &s.y)) return false;
      if (!ParseInt(t[5], &s.width)) return false;
      if (!ParseInt(t[6], &s.height)) return false;
      data->sdcs.push_back(std::move(s));
    } else if (StartsWith(line, "PATH")) {
      // Matches Python's re.findall for "( x1 y1 x2 y2 )" groups. Never fails.
      static const std::regex kEdgeRe(
          R"(\(\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\))");
      Path p;
      for (std::sregex_iterator it(line.begin(), line.end(), kEdgeRe), end;
           it != end; ++it) {
        const std::smatch& m = *it;
        Edge e;
        e.x1 = std::stoi(m[1].str());
        e.y1 = std::stoi(m[2].str());
        e.x2 = std::stoi(m[3].str());
        e.y2 = std::stoi(m[4].str());
        p.push_back(e);
      }
      data->paths.push_back(std::move(p));
    } else {
      return false;  // Unknown line.
    }
  }
  return true;
}

bool ReadJson(const std::string& path, TransplotData* data) {
  using nlohmann::json;

  std::ifstream in(path, std::ios::binary);
  if (!in) return false;

  json root;
  try {
    in >> root;
  } catch (const json::exception&) {
    return false;
  }
  if (!root.is_object()) return false;

  *data = TransplotData{};

  auto get_int = [](const json& obj, const char* key,
                    int* out) -> bool {
    auto it = obj.find(key);
    if (it == obj.end() || it->is_null() || !it->is_number()) return false;
    *out = it->get<int>();
    return true;
  };

  // canvas.* (all required; missing -> failure, matching the Python getters).
  auto canvas_it = root.find("canvas");
  if (canvas_it == root.end() || !canvas_it->is_object()) return false;
  const json& canvas = *canvas_it;

  auto die_it = canvas.find("die_area");
  if (die_it == canvas.end() || !die_it->is_object()) return false;
  std::array<int, 4> da;
  if (!get_int(*die_it, "xl", &da[0]) || !get_int(*die_it, "yl", &da[1]) ||
      !get_int(*die_it, "xh", &da[2]) || !get_int(*die_it, "yh", &da[3])) {
    return false;
  }
  data->die_area = da;

  int v;
  if (!get_int(canvas, "row_height", &v)) return false;
  data->row_height = v;
  if (!get_int(canvas, "site_width", &v)) return false;
  data->site_width = v;
  if (!get_int(canvas, "rows", &v)) return false;
  data->num_rows = v;
  if (!get_int(canvas, "sites", &v)) return false;
  data->num_sites = v;

  auto str_or = [](const json& obj, const char* key,
                   const std::string& dflt) -> std::string {
    auto it = obj.find(key);
    if (it == obj.end() || !it->is_string()) return dflt;
    return it->get<std::string>();
  };

  // ports[] (skip invalid entries).
  if (auto it = root.find("ports"); it != root.end() && it->is_array()) {
    for (const json& pj : *it) {
      Port p;
      p.name = str_or(pj, "name", "");
      p.net_name = str_or(pj, "net_name", "");
      if (!get_int(pj, "x", &p.x) || !get_int(pj, "y", &p.y) ||
          !get_int(pj, "width", &p.width) ||
          !get_int(pj, "height", &p.height)) {
        continue;
      }
      data->ports.push_back(std::move(p));
    }
  }

  // transistors[] (skip invalid; build sdc_group).
  if (auto it = root.find("transistors"); it != root.end() && it->is_array()) {
    for (const json& tj : *it) {
      Transistor tr;
      tr.name = str_or(tj, "name", "");
      bool ok_x = get_int(tj, "x", &tr.x);
      bool ok_y = get_int(tj, "y", &tr.y);
      auto type_it = tj.find("type");
      bool ok_type = type_it != tj.end() && type_it->is_string();
      if (!ok_x || !ok_y || !ok_type) continue;
      tr.type = type_it->get<std::string>();
      int flipped = 0;
      get_int(tj, "flipped", &flipped);
      tr.flipped = flipped;
      tr.sdc = str_or(tj, "sdc", "");
      data->sdc_group[tr.sdc]++;
      data->transistors.push_back(std::move(tr));
    }
  }

  // pins[] (skip invalid).
  if (auto it = root.find("pins"); it != root.end() && it->is_array()) {
    for (const json& pj : *it) {
      Pin p;
      p.name = str_or(pj, "name", "");
      p.net_name = str_or(pj, "net_name", "");
      if (!get_int(pj, "x", &p.x) || !get_int(pj, "y", &p.y)) continue;
      data->pins.push_back(std::move(p));
    }
  }

  // sdcs[] (skip invalid).
  if (auto it = root.find("sdcs"); it != root.end() && it->is_array()) {
    for (const json& sj : *it) {
      Sdc s;
      s.name = str_or(sj, "name", "");
      s.macro = str_or(sj, "macro", "");
      if (!get_int(sj, "x", &s.x) || !get_int(sj, "y", &s.y) ||
          !get_int(sj, "width", &s.width) ||
          !get_int(sj, "height", &s.height)) {
        continue;
      }
      data->sdcs.push_back(std::move(s));
    }
  }

  // paths[] (each has edges[] of {from_node:{x,y}, to_node:{x,y}}).
  if (auto it = root.find("paths"); it != root.end() && it->is_array()) {
    for (const json& pj : *it) {
      Path path_edges;
      auto edges_it = pj.find("edges");
      if (edges_it != pj.end() && edges_it->is_array()) {
        for (const json& ej : *edges_it) {
          auto from_it = ej.find("from_node");
          auto to_it = ej.find("to_node");
          if (from_it == ej.end() || to_it == ej.end()) continue;
          Edge e;
          if (!get_int(*from_it, "x", &e.x1) ||
              !get_int(*from_it, "y", &e.y1) ||
              !get_int(*to_it, "x", &e.x2) || !get_int(*to_it, "y", &e.y2)) {
            continue;
          }
          path_edges.push_back(e);
        }
      }
      data->paths.push_back(std::move(path_edges));
    }
  }

  return true;
}

bool ReadTransplot(const std::string& path, TransplotData* data) {
  if (ReadV1(path, data)) return true;
  if (ReadV2(path, data)) return true;
  if (ReadJson(path, data)) return true;
  return false;
}

}  // namespace transplot
