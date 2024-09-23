"""Transplot runner module.

Args:
    transplace_path: The path of the transplace file to read.
    plot: The plotter to use ('matplotlib' or 'cairo').
    output: The name of the png file to save the plot.
"""

import argparse
from cairo_plot import CairoPlot
from matplotlib_plot import MatplotlibPlot


def main() -> None:
    """Main function of transplot."""
    # Args parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('transplace_path')
    parser.add_argument('-o', '--output', action='store',
                        default=None, help='output png file name')
    parser.add_argument('-p', '--plot', action='store',
                        default='matplotlib',
                        help='plotter to use (`matplotlib` or `cairo`)')
    args = parser.parse_args()

    # Initialize the plotter.
    plotter = None
    if args.plot == 'matplotlib':
        plotter = MatplotlibPlot()
    elif args.plot == 'cairo':
        plotter = CairoPlot()
    else:
        print(f'[Main] Error: Unknown plotter \'{args.plot}\'.')
        return

    # Read the transplace file.
    print(f'[Main] Reading file \'{args.transplace_path}\'...')
    plotter.read(args.transplace_path)

    # Plot.
    plotter.plot(args.output)


if __name__ == '__main__':
    main()
