// Transplot runner: reads a `.tp` file and renders a PNG, mirroring
// transplot_runner.py.
//
// Only the Cairo backend is implemented in the C++ port (matplotlib has no C++
// analog); `--plot` is accepted for compatibility. Note the flag syntax follows
// Abseil conventions (e.g. `--sdc=0,1,2,3`, `--output=out.png`), unlike the
// Python argparse short flags.

#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

#include "absl/flags/flag.h"
#include "absl/flags/parse.h"
#include "absl/flags/usage.h"
#include "absl/strings/str_join.h"

#include "cairo_plot.h"
#include "reader.h"
#include "transplot_db.h"

ABSL_FLAG(std::string, output, "", "Output PNG file name");
ABSL_FLAG(std::string, plot, "cairo",
          "Plotter to use (`cairo`; `matplotlib` accepted but rendered via "
          "cairo)");
ABSL_FLAG(std::vector<std::string>, sdc, {}, "Target SDCs (comma-separated)");
ABSL_FLAG(std::vector<std::string>, transistor, {},
          "Target transistors (comma-separated)");
ABSL_FLAG(std::string, transistor_offset_x, "",
          "Transistor offset in x direction (integer)");

int main(int argc, char** argv) {
  absl::SetProgramUsageMessage(
      "transplot_runner <transplace_file> [--output=out.png] [--plot=cairo] "
      "[--sdc=0,1,...] [--transistor=t0,...] [--transistor_offset_x=N]");
  std::vector<char*> positional = absl::ParseCommandLine(argc, argv);

  if (positional.size() < 2) {
    fprintf(stderr,
            "[Main] Error: missing required positional <transplace_file>.\n");
    return 1;
  }
  const std::string transplace_path = positional[1];

  const std::string plot = absl::GetFlag(FLAGS_plot);
  if (plot != "cairo" && plot != "matplotlib") {
    fprintf(stderr,
            "[Main] Error: Unknown plotter '%s'. Use `cairo` or `matplotlib`.\n",
            plot.c_str());
    return 1;
  }
  if (plot == "matplotlib") {
    printf(
        "[Main] Note: matplotlib backend is unavailable in the C++ port; "
        "rendering with cairo.\n");
  }

  // Read the transplace file.
  printf("[Main] Reading file '%s'...\n", transplace_path.c_str());
  transplot::TransplotData data;
  if (!transplot::ReadTransplot(transplace_path, &data)) {
    fprintf(stderr, "[Main] Error: Failed to read the file '%s'.\n",
            transplace_path.c_str());
    return 1;
  }

  // Transistor offset override.
  const std::string offset_str = absl::GetFlag(FLAGS_transistor_offset_x);
  if (!offset_str.empty()) {
    data.transistor_offset = std::atoi(offset_str.c_str());
    printf("[Main] Transistor offset x: %d\n", *data.transistor_offset);
  }

  transplot::CairoPlot plotter(data);

  const std::vector<std::string> sdc = absl::GetFlag(FLAGS_sdc);
  const std::vector<std::string> transistors = absl::GetFlag(FLAGS_transistor);
  if (!sdc.empty()) {
    printf("[Main] Target SDC: %s\n", absl::StrJoin(sdc, ", ").c_str());
    plotter.SetTargetSdc(sdc);
    if (!transistors.empty()) {
      printf(
          "[Main] Warning: Target SDC is set, so the target transistors will "
          "be ignored: %s\n",
          absl::StrJoin(transistors, ", ").c_str());
    }
  } else if (!transistors.empty()) {
    printf("[Main] Target transistors: %s\n",
           absl::StrJoin(transistors, ", ").c_str());
    plotter.SetTargetTransistors(transistors);
  }

  if (!plotter.Plot(absl::GetFlag(FLAGS_output))) {
    return 1;
  }
  return 0;
}
