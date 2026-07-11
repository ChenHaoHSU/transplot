// Readers for the transplot `.tp` file, mirroring reader.py.
//
// Three dialects are supported and auto-detected in order (V1 -> V2 -> JSON),
// matching BasePlot.read(): the first reader that fully parses the file wins.

#ifndef TRANSPLOT_READER_H_
#define TRANSPLOT_READER_H_

#include <string>

#include "transplot_db.h"

namespace transplot {

// Reads `path` trying the V1, V2, then JSON dialects in order. On success fills
// `data` and returns true. Returns false if the file is missing or no dialect
// parses it (matching the Python auto-detection behavior).
bool ReadTransplot(const std::string& path, TransplotData* data);

// Individual dialect readers, exposed for testing. Each returns true iff the
// whole file parsed under that dialect.
bool ReadV1(const std::string& path, TransplotData* data);
bool ReadV2(const std::string& path, TransplotData* data);
bool ReadJson(const std::string& path, TransplotData* data);

}  // namespace transplot

#endif  // TRANSPLOT_READER_H_
