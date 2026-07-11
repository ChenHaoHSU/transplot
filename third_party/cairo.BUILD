# Wraps the prebuilt static Cairo stack shipped in the conda `transplot` env.
# Link order is expressed through the deps graph: cairo -> pixman -> png -> z.
# Only -lm is needed as an extra system lib (pthread is folded into glibc 2.39).
#
# NOTE: this does NOT pull freetype/fontconfig. libcairo.a's monolithic
# cairo.c.o references the toy-font backend (dead code for us), which drags in
# ~52 FT_*/Fc* symbols; those are satisfied by //:cairo_font_stubs in the main
# BUILD, keeping the binary fully static without the (unavailable) font static
# archives.

package(default_visibility = ["//visibility:public"])

cc_import(
    name = "z",
    static_library = "lib/libz.a",
)

cc_import(
    name = "png16",
    static_library = "lib/libpng16.a",
)

cc_import(
    name = "pixman",
    static_library = "lib/libpixman-1.a",
)

cc_import(
    name = "cairo_archive",
    static_library = "lib/libcairo.a",
)

cc_library(
    name = "cairo",
    hdrs = glob(["include/cairo/*.h"]),
    includes = ["include/cairo"],
    linkopts = ["-lm"],
    deps = [
        ":cairo_archive",
        ":pixman",
        ":png16",
        ":z",
    ],
)
