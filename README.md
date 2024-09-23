# Transplot Instruction

To use the Transplot tool, follow these steps:

Run the main script:
  ```
  python3 transplot_runner.py <transplace_filename>
      [-p, --plot <matplotlib | cairo>]
      [-o, --output <output_png_filename>]
      [-s, --sdc <sdc0, ...>]
      [-t, --transistor <t0, ...>]
  ```

  ### Example Usage
  1. Basic usage with default settings (plot=matplotlib, output=None):
```
python3 transplot_runner.py example/example1.tp
```

  2. Save the output as a PNG file (plot=matplotlib, output=example1.png):
```
python3 transplot_runner.py example/example1.tp -o example1.png
```

  3. Use a specific plotter (plot=cairo, output=None):
```
python3 transplot_runner.py example/example1.tp -p cairo
```

  4. Combine options (plot=cairo, output=example1.png):
```
python3 transplot_runner.py example/example1.tp -p cairo -o example1.png
```

  5. Set the target SDCs.
```
python3 transplot_runner.py example/example1.tp -p cairo -o example1.png -s 0 1 2 3
```

  6. Set the target transistors.
```
python3 transplot_runner.py example/example1.tp -p cairo -o example1.png -t MMP2_add_4_U1_0_inst0_MM20
```
