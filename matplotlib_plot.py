"""A module to visualize transistor placement using Matplotlib.

This module extends the BasePlot class and implements the plot method using
the Matplotlib library.
"""

from typing import Any, List, Dict, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from base_plot import BasePlot


class MatplotlibRect:
    """A class to represent a plot object (rectangle) using Matplotlib."""

    def __init__(self, x: int, y: int, w: int, h: int,
                 alpha: float = 1.0,
                 fill: bool = True,
                 fill_rgb: Tuple[float, float, float] = (1., 1., 1.),
                 edge: bool = False,
                 edge_rgb: Tuple[float, float, float] = (0., 0., 0.),
                 linewidth: int = 1):
        """Initializes the MatplotlibRect object.

        Args:
            x: x-coordinate of the top-left corner of the rectangle
            y: y-coordinate of the top-left corner of the rectangle
            w: Width of the rectangle
            h: Height of the rectangle
            alpha: Alpha value (transparency) of the rectangle (default is 1.0)
            fill: Whether to fill the rectangle (default is True)
            fill_rgba: Fill color of the rectangle (R, G, B)
            edge: Whether to outline the rectangle (default is False)
            edge_rgba: Outline color of the rectangle (R, G, B)
            linewidth: Width of the outline (default is 1)
        """
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.alpha = alpha
        self.fill = fill
        self.fill_rgb = fill_rgb
        self.edge = edge
        self.edge_rgb = edge_rgb
        self.linewidth = linewidth

    def __repr__(self):
        return f'MatplotlibRect(x={self.x}, y={self.y}, w={self.w}, ' \
               f'h={self.h}, alpha={self.alpha}, fill={self.fill}, ' \
               f'fill_rgb={self.fill_rgb}, edge_rgb={self.edge_rgb}, ' \
               f'linewidth={self.linewidth})'

    def draw(self, ax: plt.Axes) -> None:
        """Draws the rectangle on the given Matplotlib Axes.

        This method draws the rectangle on the given Matplotlib Axes with the
        specified fill and edge colors.

        Args:
            ax: A Matplotlib Axes to draw the rectangle on.
        """
        fill = self.fill
        facecolor = self.fill_rgb if self.fill else None
        edgecolor = self.edge_rgb if self.edge else None
        rect = Rectangle((self.x, self.y), self.w, self.h,
                         alpha=self.alpha, fill=fill,
                         facecolor=facecolor, edgecolor=edgecolor)
        ax.add_patch(rect)


class MatplotlibPlot(BasePlot):
    """A class to visualize transistor placement using Matplotlib.

    This class extends the BasePlot class and implements the plot method using
    the Matplotlib library.

    Typical usage example:

        plotter = MatplotlibPlot()
        plotter.read('example.tp')
        plotter.plot('example.png')
    """

    def __init__(self):
        super().__init__()
        self.params: Dict[str, Any] = {
            # RGB color of row edges.
            'row_edge_rgb': (0, 0, 0),
            # Width of row edges.
            'row_linewidth': 1.0,
            # Width of transistors.
            'transistor_width': 1728,
            # Height of transistors.
            'transistor_height': 3456,
            # RGB color of inverter fill.
            'transistor_fill_rgb_inv': (8, 8, 8),
            # RGB color of transistor edges.
            'transistor_edge_rgb': (0, 0, 0),
            # Width of transistor edges.
            'transistor_linewidth': 0.8,
            # Fill alpha of transistors.
            'transistor_alpha': {'NMOS': 0.9, 'PMOS': 0.5},
            # Fill alpha of inverters.
            'transistor_alpha_inv': {'NMOS': 0.4, 'PMOS': 0.25},
            # Shrink ratio of poly.
            'transistor_poly_shrink_ratio': 0.2,
            # Shrink ratio of diffusion.
            'transistor_diffusion_shrink_ratio': 0.5,
        }

    def generate_row_rectangles(self) -> List[MatplotlibRect]:
        """Generates plot rectangles for rows.

        @return: A list of MatplotlibRect objects representing rows.
        """
        if not self.data['die_area'] or not self.data['row_height']:
            return []

        die_xl, die_yl, die_xh, _ = tuple(self.data['die_area'])

        row_start_x = die_xl
        row_start_y = die_yl
        row_width = die_xh - die_xl
        row_height = self.data['row_height']
        row_edge_rgb = self._convert_int_to_float_rgb(
            self.params['row_edge_rgb'])
        row_linewidth = self.params['row_linewidth']

        def gen_rect(i: int) -> MatplotlibRect:
            return MatplotlibRect(
                x=row_start_x, y=row_start_y + i * row_height, w=row_width,
                h=row_height, fill=False, edge=True, edge_rgb=row_edge_rgb,
                linewidth=row_linewidth)

        rectangles = []
        for i in range(self.data['num_rows']):
            # i is the row index, and it determines the y-coordinate of the row.
            rectangles.append(gen_rect(i))

        return rectangles

    def generate_transistor_rectangles(self) -> List[MatplotlibRect]:
        """Generates plot rectangles for transistors.

        Returns:
            A list of MatplotlibRect objects representing transistors.
        """
        tran_width = self.params['transistor_width']
        tran_height = self.params['transistor_height']

        def gen_rect(
                transistor: Dict[str, Any]) -> List[MatplotlibRect]:
            # Transistor location (scaled).
            tran_x = transistor['x']
            tran_y = transistor['y']

            # Fill.
            # Inverter: black. Others: random color.
            tran_type = transistor['type']
            fill_rgb, fill_alpha = (0, 0, 0), 1.0
            if self.data['sdc_group'][transistor['sdc']] <= 2:
                fill_rgb = self._convert_int_to_float_rgb(
                    self.params['transistor_fill_rgb_inv'])
                fill_alpha = self.params['transistor_alpha_inv'][tran_type]
            else:
                fill_rgb = self._convert_int_to_float_rgb(
                    self.colors[transistor['sdc'] % len(self.colors)])
                fill_alpha = self.params['transistor_alpha'][tran_type]

            # Edge.
            edge_rgb = self._convert_int_to_float_rgb(
                self.params['transistor_edge_rgb'])
            linewidth = self.params['transistor_linewidth']

            # Diffusion rectangle.
            diff_shrink_ratio = self.params['transistor_diffusion_shrink_ratio']
            diff_y = tran_y + (tran_height * (1 - diff_shrink_ratio) / 2)
            diff_height = tran_height * diff_shrink_ratio
            diffusion_rect = MatplotlibRect(
                x=tran_x, y=diff_y, w=tran_width, h=diff_height,
                alpha=fill_alpha, fill=True, fill_rgb=fill_rgb,
                edge=True, edge_rgb=edge_rgb, linewidth=linewidth)

            # Poly rectangle.
            poly_shrink_ratio = self.params['transistor_poly_shrink_ratio']
            poly_x = tran_x + (tran_width * (1 - poly_shrink_ratio) / 2)
            poly_width = tran_width * poly_shrink_ratio
            poly_rect = MatplotlibRect(
                x=poly_x, y=tran_y, w=poly_width, h=tran_height,
                alpha=fill_alpha, fill=True, fill_rgb=fill_rgb,
                edge=True, edge_rgb=edge_rgb, linewidth=linewidth)

            return [diffusion_rect, poly_rect]

        rectangles = []
        for transistor in self.data['transistors']:
            rectangles.extend(gen_rect(transistor))

        return rectangles

    def get_plot_boundary(self) -> Tuple[int, int, int, int]:
        """Gets the boundary of the plot.

        Returns:
            A tuple of (x_low, y_low, x_high, y_high)
        """
        if not self.data['die_area']:
            return (0, 0, 0, 0)

        die_xl, die_yl, die_xh, die_yh = tuple(self.data['die_area'])
        return (die_xl, die_yl, die_xh, die_yh)

    def plot(self, png_name: str = None) -> None:
        """Plots the data to a pop-up window or save to a png file.

        This method plots the data using Matplotlib. If png_name is provided,
        the plot will be saved to a png file with the given name. Otherwise, the
        plot will be shown in a pop-up window.

        Args:
            png_name: Name of the png file to save the plot.
              If None, show in a pop-up window.
        """
        print('[MatplotlibPlot] Plotting data using Matplotlib')

        # Generate rectangles for rows.
        print('[MatplotlibPlot] Generating row rectangles...')
        row_rectangles = self.generate_row_rectangles()

        # Generate rectangles for transistors.
        print('[MatplotlibPlot] Generating transistor rectangles...')
        transistor_rectangles = self.generate_transistor_rectangles()

        # Create a plot.
        print('[MatplotlibPlot] Creating plot... (This may take a few seconds)')
        _, ax = plt.subplots()

        # Draw the objects.
        for obj in row_rectangles:
            obj.draw(ax)
        for obj in transistor_rectangles:
            obj.draw(ax)

        # Set the plot limits.
        plot_xl, plot_yl, plot_xh, plot_yh = self.get_plot_boundary()
        plt.xlim([plot_xl, plot_xh])
        plt.ylim([plot_yl, plot_yh])

        # Turn off the axis.
        plt.axis('off')

        # Save to a png file or show in a pop-up window.
        if png_name:
            plt.savefig(png_name, dpi=400)
            print(f'[MatplotlibPlot] Image saved to \'{png_name}\'.')
        else:
            print('[MatplotlibPlot] Showing plot in a pop-up window...')
            plt.show()
