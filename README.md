# Transplot

[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](LICENSE)
[![Language: C++17](https://img.shields.io/badge/C%2B%2B-17-00599C.svg)](https://isocpp.org/)
[![Build: Bazel](https://img.shields.io/badge/build-Bazel-43A047.svg)](https://bazel.build/)

**Transplot** is a tiny visualizer for transistor placement. It reads a `.tp`
placement file and renders a PNG of the layout — placement rows, transistors
(diffusion + poly, colored by SDC group), ports, pins, SDC/macro boxes, and
routing paths.

<!-- Add a rendered example image here, e.g.: -->
<!-- ![example](docs/example1.png) -->

There are two implementations in this repo:

- A **C++ port** (recommended) that builds as a single **fully static** binary
  with [Bazel](https://bazel.build/) and renders **pixel-identical** output to
  the original.
- The **original Python tool** under [`python/`](python/).

---

## Table of contents

- [Features](#features)
- [Quick start](#quick-start)
- [Usage](#usage)
- [The `.tp` file format](#the-tp-file-format)
- [How it works](#how-it-works)
- [Project layout](#project-layout)
- [Building and testing](#building-and-testing)
- [License](#license)

## Features

- **Three input dialects, auto-detected** — V1 (block form), V2
  (keyword-per-line), and JSON.
- **SDC-group coloring** — transistor groups larger than two transistors get a
  distinct color; smaller groups render as gray "inverter" cells. PMOS/NMOS are
  distinguished by opacity.
- **Deterministic output** — the color palette is reproducible run to run.
- **Static, dependency-free binary** — Cairo is linked statically, so the
  resulting executable has no shared-library dependencies.
- **Pixel-identical parity** — the C++ and Python renderers produce byte-for-byte
  identical PNGs.

## Quick start

```sh
# Build the statically-linked binary.
bazel build //:transplot_runner

# Render an example.
bazel-bin/transplot_runner example/example1.tp --output=example1.png
```

That's it — `example1.png` now contains the rendered layout.

## Usage

```
transplot_runner <file.tp> [flags]
```

| Flag | Description | Default |
|------|-------------|---------|
| `<file.tp>` | Input placement file (positional, required) | — |
| `--output=<path>` | Output PNG path | `cairo_plot.png` |
| `--plot=<cairo\|matplotlib>` | Backend (only `cairo` is implemented; `matplotlib` falls back to it) | `cairo` |
| `--sdc=<a,b,c>` | Highlight only these SDC groups (comma-separated) | all |
| `--transistor=<t0,t1>` | Highlight only these transistors by name | all |
| `--transistor_offset_x=<N>` | Shift transistors/pins in x | none |

Examples:

```sh
# Basic render.
bazel-bin/transplot_runner example/example1.tp --output=example1.png

# Highlight specific SDC groups; everything else is drawn gray.
bazel-bin/transplot_runner example/example1.tp --output=out.png --sdc=0,1,2,3

# Highlight a single transistor by name.
bazel-bin/transplot_runner example/example1.tp --output=out.png \
    --transistor=MMP2_add_4_U1_0_inst0_MM20
```

<details>
<summary>Using the original Python tool</summary>

The Python implementation lives in [`python/`](python/) and supports both a
`cairo` and a `matplotlib` backend. Its CLI uses argparse-style flags:

```sh
python3 python/transplot_runner.py <file.tp> \
    [-p, --plot <matplotlib | cairo>] \
    [-o, --output <output.png>] \
    [-s, --sdc <sdc0 ...>] \
    [-t, --transistor <t0 ...>]

# Examples
python3 python/transplot_runner.py example/example1.tp
python3 python/transplot_runner.py example/example1.tp -p cairo -o example1.png
python3 python/transplot_runner.py example/example1.tp -p cairo -s 0 1 2 3
```

Dependencies are captured in [`environment.yml`](environment.yml)
(`conda env create -f environment.yml`).
</details>

## The `.tp` file format

A `.tp` file is line-oriented; each line begins with a keyword. Coordinates are
integers in database units. Header directives are shared across dialects:

```
UNITS      <int>                # database units per micron
DIEAREA    <xl> <yl> <xh> <yh>  # die bounding box
ROWHEIGHT  <int>                # standard-cell row height
SITEWIDTH  <int>                # placement site width
ROWS       <int>                # number of rows
SITES      <int>                # sites per row
```

The two text dialects differ in how objects are listed:

- **V1** wraps transistors in a counted block:
  ```
  TRANSISTORS <n>
  <name> <x> <y> <flipped> <type> <sdc>
  ...
  END TRANSISTORS
  ```
- **V2** uses one keyword line per object and supports more object types:
  ```
  PORT       <name> <net> <x> <y> <width> <height>
  TRANSISTOR <name> <x> <y> <flipped> <type> <sdc>
  PIN        <name> <x> <y> <net>
  SDC        <name> <macro> <x> <y> <width> <height>
  PATH       ( x1 y1 x2 y2 ) ( x1 y1 x2 y2 ) ...
  ```

A JSON variant is also accepted (`canvas`, `transistors`, `ports`, `pins`,
`sdcs`, `paths`). See [`example/`](example/) for complete samples and
[`reader.h`](reader.h) for the authoritative grammar.

## How it works

The renderer draws a fixed 2000×2000 canvas, fits the die (plus a margin) with a
uniform scale, and paints in a fixed order: rows → ports → transistors → pins →
SDC boxes → paths.

Because [Cairo](https://www.cairographics.org/) has no Bazel Central Registry
module and the build host has no meson/ninja, Cairo is linked from prebuilt
static archives (see [`third_party/cairo.BUILD`](third_party/cairo.BUILD)).
Cairo's monolithic object references its toy-font backend, which pulls in
freetype/fontconfig symbols even though the tool renders no text; those symbols
are satisfied by no-op stubs in [`cairo_font_stubs.c`](cairo_font_stubs.c),
keeping the binary fully static without the font libraries.

## Project layout

```
transplot/
├── transplot_runner.cc     # CLI entry point (C++)
├── reader.{h,cc}           # V1 / V2 / JSON parsers
├── base_plot.{h,cc}        # SDC color map + highlight filtering
├── cairo_plot.{h,cc}       # Cairo renderer
├── python_random.{h,cc}    # CPython-compatible RNG (color parity)
├── cairo_font_stubs.c      # static-link shim for Cairo's font backend
├── transplot_db.h          # shared data structures
├── third_party/cairo.BUILD # static Cairo wiring
├── example/                # sample .tp files
└── python/                 # original Python implementation
```

## Building and testing

Requires [Bazel](https://bazel.build/) (see [`.bazelversion`](.bazelversion));
`bazelisk` will pick up the pinned version automatically.

```sh
bazel build //:transplot_runner   # build the static binary
bazel test  //...                 # run the reader + RNG unit tests
```

Verify the binary is standalone:

```sh
file bazel-bin/transplot_runner   # ... statically linked ...
ldd  bazel-bin/transplot_runner   # not a dynamic executable
```

## License

This project is released into the public domain under
[The Unlicense](LICENSE). You may copy, modify, publish, use, compile, sell, or
distribute it, for any purpose, with or without attribution.
