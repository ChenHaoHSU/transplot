# Transplot Instruction

To use the Transplot tool, follow these steps:

Run the main script:
  ```
  python3 transplot_runner.py <transplace_filename>
      [--plotter <matplotlib | cairo>]
      [--png <png_filename>]
  ```

  ### Example Usage
  1. Basic usage with default settings (plotter=matplotlib, png=None):
```
python3 transplot_runner.py example/example1.tp
```

  3. Save the output as a PNG file (plotter=matplotlib, png=example1.png):
```
python3 transplot_runner.py example/example1.tp --png example1.png
```

  4. Use a specific plotter (e.g., Cairo):
```
python3 transplot_runner.py example/example1.tp --plotter cairo
```

  5. Combine options:
```
python3 transplot_runner.py example/example1.tp --plotter cairo --png example1.png
```
