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
                 linewidth: float = 1.0):
        """Initializes the MatplotlibRect object.

        Args:
            x: x-coordinate of the bottom-left corner of the rectangle.
            y: y-coordinate of the bottom-left corner of the rectangle.
            w: Width of the rectangle.
            h: Height of the rectangle.
            alpha: Alpha value (transparency) of the rectangle. (default is 1.0)
            fill: Whether to fill the rectangle. (default is True)
            fill_rgba: Fill color of the rectangle. (R, G, B)
            edge: Whether to outline the rectangle. (default is False)
            edge_rgba: Outline color of the rectangle. (R, G, B)
            linewidth: Width of the outline. (default is 1.0)
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
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=self.linewidth)
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
            'row_linewidth': 0.5,
            # Gray color fill.
            'transistor_fill_rgb_gray': (8, 8, 8),
            # RGB color of transistor edges.
            'transistor_edge_rgb': (0, 0, 0),
            # Width of transistor edges.
            'transistor_linewidth': 0.3,
            # Fill alpha of transistors.
            'transistor_alpha': {'NMOS': 0.5, 'PMOS': 0.9},
            # Fill alpha of inverters.
            'transistor_alpha_inv': {'NMOS': 0.4, 'PMOS': 0.25},
            # Shrink ratio of poly.
            'transistor_poly_shrink_ratio': 0.2,
            # Shrink ratio of diffusion.
            'transistor_diffusion_shrink_ratio': 0.5,
            # Plot margin x.
            'plot_margin_x': 2000,
            # Plot margin y.
            'plot_margin_y': 2000,
            # Width of transistors (unused, use `site_width` instead).
            # 'transistor_width': 1728,
            # Height of transistors (unused, use `row_height / 2` instead).
            # 'transistor_height': 3456,
        }

    def _generate_row_rectangles(self) -> List[MatplotlibRect]:
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

        def generate_one_row_rectangle(i: int) -> MatplotlibRect:
            return MatplotlibRect(
                x=row_start_x, y=row_start_y + i * row_height, w=row_width,
                h=row_height, fill=False, edge=True, edge_rgb=row_edge_rgb,
                linewidth=row_linewidth)

        rectangles = []
        for i in range(self.data['num_rows']):
            # i is the row index, and it determines the y-coordinate of the row.
            rectangles.append(generate_one_row_rectangle(i))

        return rectangles

    def _generate_transistor_rectangles(self) -> List[MatplotlibRect]:
        """Generates plot rectangles for transistors.

        Returns:
            A list of MatplotlibRect objects representing transistors.
        """
        # Trasistor size.
        tran_width = self.data['site_width']
        tran_height = self.data['row_height'] / 2  # Half of the SDC height.

        # Edge.
        edge_rgb = self._convert_int_to_float_rgb(
            self.params['transistor_edge_rgb'])
        linewidth = self.params['transistor_linewidth']

        diff_shrink_ratio = self.params['transistor_diffusion_shrink_ratio']
        diff_y_offset = tran_height * (1 - diff_shrink_ratio) / 2
        diff_height = tran_height * diff_shrink_ratio

        poly_shrink_ratio = self.params['transistor_poly_shrink_ratio']
        poly_x_offset = tran_width * (1 - poly_shrink_ratio) / 2
        poly_width = tran_width * poly_shrink_ratio

        def get_fill_rgba(
                transistor: Dict[str, Any]
        ) -> Tuple[Tuple[float, float, float], float]:
            # Inverter: black. Others: colors from the color map.
            tran_type = transistor['type']
            fill_rgb, fill_alpha = (0, 0, 0), 1.0
            if self._is_transistor_to_color_plot(transistor):
                assert transistor['sdc'] in self.color_map
                fill_rgb = self._convert_int_to_float_rgb(
                    self.color_map[transistor['sdc']])
                fill_alpha = self.params['transistor_alpha'][tran_type]
            else:
                fill_rgb = self._convert_int_to_float_rgb(
                    self.params['transistor_fill_rgb_gray'])
                fill_alpha = self.params['transistor_alpha_inv'][tran_type]
            return fill_rgb, fill_alpha

        def generate_one_transistor_rectangles(
                transistor: Dict[str, Any]) -> List[MatplotlibRect]:
            # Transistor location.
            tran_x, tran_y = transistor['x'],  transistor['y']

            # Fill.
            # Inverter: black. Others: random color.
            fill_rgb, fill_alpha = get_fill_rgba(transistor)

            # Diffusion rectangle.
            diffusion_rect = MatplotlibRect(
                x=tran_x, y=tran_y + diff_y_offset, w=tran_width, h=diff_height,
                alpha=fill_alpha, fill=True, fill_rgb=fill_rgb,
                edge=True, edge_rgb=edge_rgb, linewidth=linewidth)

            # Poly rectangle.
            poly_rect = MatplotlibRect(
                x=tran_x + poly_x_offset, y=tran_y, w=poly_width, h=tran_height,
                alpha=fill_alpha, fill=True, fill_rgb=fill_rgb,
                edge=True, edge_rgb=edge_rgb, linewidth=linewidth)

            return [diffusion_rect, poly_rect]

        rectangles = []
        for transistor in self.data['transistors']:
            rectangles.extend(generate_one_transistor_rectangles(transistor))

        return rectangles

    def _get_plot_boundary(self) -> Tuple[int, int, int, int]:
        """Gets the boundary of the plot.

        This method calculates the boundary of the plot based on the die area
        and the plot margin.

        Returns:
            A tuple of (x_low, y_low, x_high, y_high)
        """
        if not self.data['die_area']:
            return (0, 0, 0, 0)

        plot_margin_x = self.params['plot_margin_x']
        plot_margin_y = self.params['plot_margin_y']
        die_xl, die_yl, die_xh, die_yh = tuple(self.data['die_area'])

        return (die_xl - plot_margin_x, die_yl - plot_margin_y,
                die_xh + plot_margin_x, die_yh + plot_margin_y)

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
        row_rectangles = self._generate_row_rectangles()

        # Generate rectangles for transistors.
        print('[MatplotlibPlot] Generating transistor rectangles...')
        transistor_rectangles = self._generate_transistor_rectangles()

        # Create a plot.
        print('[MatplotlibPlot] Creating plot... (This may take a few seconds)')
        _, ax = plt.subplots()

        # Draw the objects.
        for obj in row_rectangles:
            obj.draw(ax)
        for obj in transistor_rectangles:
            obj.draw(ax)

        # Set the plot limits.
        plot_xl, plot_yl, plot_xh, plot_yh = self._get_plot_boundary()
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
