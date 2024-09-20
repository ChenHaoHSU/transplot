"""
A tool to visualize transistor placement.
"""

import argparse
import random
from transplot import Transplot


def main() -> None:
    """
    Main function of transplot
    """
    # Args parser.
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument(
        "focus_id",
        metavar="focus_id",
        nargs="*",
        help="specify std cell IDs to be colored",
    )
    parser.add_argument("--savefig", action="store",
                        default=None, help="save to png")
    args = parser.parse_args()

    # Read the transplace file.
    transplot = Transplot()
    transplot.read(args.filename)

    transplot.plot()


if __name__ == "__main__":
    main()
