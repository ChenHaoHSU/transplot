# Transplot Instruction

To use the Transplot tool, follow these steps:

Run the main script:
  ```bash
  python3 transplot_runner.py <transplace_filename>
      [--plotter <matplotlib | cairo>]
      [--png <png_filename>]
  ```

  ### Example Usage
  1. Basic usage with default settings (plotter=matplotlib, png=None):
    ```bash
    python3 transplot_runner.py example/example1.tp
    ```

  2. Save the output as a PNG file (plotter=matplotlib, png=example1.png):
    ```bash
    python3 transplot_runner.py example/example1.tp --png example1.png
    ```

  3. Use a specific plotter (e.g., Cairo):
    ```bash
    python3 transplot_runner.py example/example1.tp --plotter cairo
    ```

  4. Combine options:
    ```bash
    python3 transplot_runner.py example/example1.tp --plotter cairo --png example1.png
    ```