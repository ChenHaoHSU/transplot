"""Transplot runner module.

Args:
    transplace_path: The path of the transplace file to read. (Required)
    plot: The plotter to use ('matplotlib' or 'cairo'). Default is 'matplotlib'.
        (Optional)
    output: The name of the png file (*.png) to save the plot. (Optional)
    sdc: The target SDC. If not set, all SDCs are color plotted. (Optional)
    transistor: The target transistors. If not set, all transistors are color
        plotted. (Optional)
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
    parser.add_argument('-s', '--sdc', action='store',
                        nargs="*", default=None, help='target SDCs')
    parser.add_argument('-t', '--transistor', action='store',
                        nargs="*", default=None, help='target transistors')
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

    # Set the target SDC or transistors.
    if args.sdc:
        # Set the target SDC.
        print(f'[Main] Target SDC: {args.sdc}')
        plotter.set_target_sdc(args.sdc)
        if args.transistor:
            print('[Main] Warning: Target SDC is set, so the target '
                  f'transistors will be ignored: {args.transistor}')
    elif args.transistor:
        # Set the target transistors.
        print(f'[Main] Target transistors: {args.transistor}')
        plotter.set_target_transistors(args.transistor)

    # Plot.
    plotter.plot(args.output)


if __name__ == '__main__':
    main()
