"""Transplot runner module.

Args:
    filename: The name of the transplace file to read.
    focus_id: The std cell IDs to be colored.
    png: The name of the png file to save the plot.
    plotter: The plotter to use ('matplotlib' or 'cairo').
"""

import argparse
from cairo_plot import CairoPlot
from matplotlib_plot import MatplotlibPlot


def main() -> None:
    """Main function of transplot."""
    # Args parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument(
        'focus_id',
        metavar='focus_id',
        nargs='*',
        help='specify std cell IDs to be colored',
    )
    parser.add_argument('--png', action='store',
                        default=None, help='png file name')
    parser.add_argument('--plotter', action='store',
                        default='matplotlib',
                        help='plotter to use (matplotlib or cairo)')
    args = parser.parse_args()

    # Initialize the plotter.
    plotter = None
    if args.plotter == 'matplotlib':
        plotter = MatplotlibPlot()
    elif args.plotter == 'cairo':
        plotter = CairoPlot()
    else:
        print(f'[Main] Error: Unknown plotter \'{args.plotter}\'.')
        return

    # Read the transplace file.
    print(f'[Main] Reading file \'{args.filename}\'...')
    plotter.read(args.filename)

    # Plot.
    plotter.plot(args.png)


if __name__ == '__main__':
    main()
