# Transplot Instruction

To use the Transplot tool, follow these steps:

Run the main script:
  ```
  python3 transplot_runner.py <transplace_filename>
      [-p, --plot <matplotlib | cairo>]
      [-o, --output <output_png_filename>]
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

  5. Set target SDC.
```
python3 transplot_runner.py example/example1.tp -p cairo -o example1.png -s 0 1 2 3
```
