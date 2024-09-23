"""A module to visualize transistor placement using Cairo.

This module extends the BasePlot class and implements the plot method using
the Cairo graphics library.
"""

from typing import Any, List, Dict, Tuple
import cairo
from base_plot import BasePlot


class CairoRect:
    """A class to represent a plot object (rectangle) using Cairo."""

    def __init__(
            self, x: int, y: int, w: int, h: int,
            fill: bool = True,
            fill_rgba: Tuple[float, float, float, float] = (1., 1., 1., 1.),
            stroke: bool = False,
            stroke_rgba: Tuple[float, float, float, float] = (0., 0., 0., 1.),
            linewidth: float = 1.0):
        """Initializes the CairoRect object.

        Args:
            x: x-coordinate of the bottom-left corner of the rectangle.
            y: y-coordinate of the bottom-left corner of the rectangle.
            w: Width of the rectangle.
            h: Height of the rectangle.
            fill: Whether to fill the rectangle. (default is True)
            fill_rgba: Fill color of the rectangle. (R, G, B, A)
            stroke: Whether to outline the rectangle. (default is False)
            stroke_rgba: Stroke color of the rectangle. (R, G, B, A)
            linewidth: Width of the stroke line. (default is 1.0)
        """
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.fill = fill
        self.fill_rgba = fill_rgba
        self.stroke = stroke
        self.stroke_rgba = stroke_rgba
        self.linewidth = linewidth

    def __repr__(self):
        return f'CairoRect(x={self.x}, y={self.y}, w={self.w}, ' \
            f'h={self.h}, fill={self.fill}, fill_rgba={self.fill_rgba}, ' \
            f'stroke={self.stroke}, stroke_rgba={self.stroke_rgba}, ' \
            f'linewidth={self.linewidth})'

    def draw(self, context: cairo.Context) -> None:
        """Draws the rectangle on the given Cairo context.

        This method draws the rectangle on the given Cairo context with the
        specified fill and stroke properties.

        Args:
            context: A Cairo context to draw the rectangle on.
        """
        # Set fill color and fill the rectangle if enabled
        if self.fill:
            context.set_source_rgba(*self.fill_rgba)
            context.rectangle(self.x, self.y, self.w, self.h)
            if self.stroke:
                context.fill_preserve()  # Fill and preserve for stroking
            else:
                context.fill()  # Just fill the rectangle

        # Set stroke color and stroke the rectangle if enabled
        if self.stroke:
            context.set_source_rgba(*self.stroke_rgba)
            context.set_line_width(self.linewidth)
            context.rectangle(self.x, self.y, self.w, self.h)
            context.stroke()


class CairoPlot(BasePlot):
    """A class to visualize transistor placement using Cairo.

    This class extends the BasePlot class and implements the plot method using
    the Cairo graphics library.

    Typical usage example:

        plotter = CairoPlot()
        plotter.read('example.tp')
        plotter.plot('example.png')
    """

    # Default name of the png file to save the plot.
    DEFAULT_PNG_NAME = 'cairo_plot.png'

    def __init__(self):
        super().__init__()
        self.params: Dict[str, Any] = {
            # RGB color of row edges.
            'row_stroke_rgba': (0, 0, 0, 1),
            # Width of row edges.
            'row_linewidth': 1.0,
            # Width of transistors.
            'transistor_width': 1728,
            # Height of transistors.
            'transistor_height': 3456,
            # RGB color of transistor edges.
            'transistor_stroke_rgb': (0, 0, 0),
            # Alpha of transistor edges.
            'transistor_stroke_alpha': 1.0,
            # Width of transistor edges.
            'transistor_linewidth': 1.0,
            # Fill alpha of transistors.
            'transistor_alpha': {'NMOS': 0.9, 'PMOS': 0.5},
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
        }

    def _generate_row_rectangles(self) -> List[CairoRect]:
        """Generates plot rectangles for rows.

        Returns:
            A list of CairoRect objects representing rows.
        """
        if not self.data['die_area'] or not self.data['row_height']:
            return []

        die_xl, die_yl, die_xh, _ = tuple(self.data['die_area'])

        row_start_x = die_xl
        row_start_y = die_yl
        row_width = die_xh - die_xl
        row_height = self.data['row_height']

        def _generate_one_row_rectangle(i: int) -> CairoRect:
            return CairoRect(x=row_start_x, y=row_start_y + i * row_height,
                             w=row_width, h=row_height,
                             fill=False,
                             stroke=True,
                             stroke_rgba=self.params['row_stroke_rgba'],
                             linewidth=self.params['row_linewidth'])

        rectangles = []
        for i in range(self.data['num_rows']):
            rectangles.append(_generate_one_row_rectangle(i))

        return rectangles

    def _generate_transistor_rectangles(self) -> List[CairoRect]:
        """Generates plot rectangles for transistors.

        Returns:
            A list of CairoRect objects representing transistors.
        """
        # Transistor size.
        tran_width = self.params['transistor_width']
        tran_height = self.params['transistor_height']

        # Stroke.
        stroke_rgb = self._convert_int_to_float_rgb(
            self.params['transistor_stroke_rgb'])
        stroke_rgba = stroke_rgb + (self.params['transistor_stroke_alpha'],)
        linewidth = self.params['transistor_linewidth']

        diff_shrink_ratio = self.params['transistor_diffusion_shrink_ratio']
        diff_y_offset = tran_height * (1 - diff_shrink_ratio) / 2
        diff_height = tran_height * diff_shrink_ratio

        poly_shrink_ratio = self.params['transistor_poly_shrink_ratio']
        poly_x_offset = tran_width * (1 - poly_shrink_ratio) / 2
        poly_width = tran_width * poly_shrink_ratio

        def get_fill_rgba(
                transistor: Dict[str, Any]
        ) -> Tuple[float, float, float, float]:
            # Inverter: black. Others: colors from the color map.
            tran_type = transistor['type']
            fill_rgb, fill_alpha = (0, 0, 0), 1.0
            if self.data['sdc_group'][transistor['sdc']] <= 2:
                fill_rgb = self._convert_int_to_float_rgb((8, 8, 8))
                fill_alpha = self.params['transistor_alpha_inv'][tran_type]
            else:
                assert transistor['sdc'] in self.color_map
                fill_rgb = self._convert_int_to_float_rgb(
                    self.color_map[transistor['sdc']])
                fill_alpha = self.params['transistor_alpha'][tran_type]
            return fill_rgb + (fill_alpha,)

        def generate_one_transistor_rectangles(
                transistor: Dict[str, Any]) -> List[CairoRect]:
            # Transistor location.
            tran_x = transistor['x']
            tran_y = transistor['y']

            # Fill.
            fill_rgba = get_fill_rgba(transistor)

            # Diffusion rectangle.
            diffusion_rect = CairoRect(
                x=tran_x, y=tran_y + diff_y_offset, w=tran_width, h=diff_height,
                fill=True, fill_rgba=fill_rgba, stroke=True,
                stroke_rgba=stroke_rgba, linewidth=linewidth)

            # Poly rectangle.
            poly_rect = CairoRect(
                x=tran_x + poly_x_offset, y=tran_y, w=poly_width, h=tran_height,
                fill=True, fill_rgba=fill_rgba, stroke=True,
                stroke_rgba=stroke_rgba, linewidth=linewidth)

            return [diffusion_rect, poly_rect]

        rectangles = []
        for transistor in self.data['transistors']:
            rectangles.extend(generate_one_transistor_rectangles(transistor))

        return rectangles

    def _get_die_area(self) -> Tuple[int, int, int, int]:
        """Gets the die area.

        Returns:
            A tuple of (x_low, y_low, x_high, y_high)
        """
        if not self.data['die_area']:
            return (0, 0, 0, 0)
        return tuple(self.data['die_area'])

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

    def _adjust_linewidth(self, scale_factor: float) -> None:
        """Adjusts the linewidth based on the scale factor.

        Args:
            scale_factor: The scale factor used to adjust the linewidth.
        """
        self.params['row_linewidth'] /= scale_factor
        self.params['transistor_linewidth'] /= scale_factor

    def plot(self, png_name: str = None) -> None:
        """Plots the data to a pop-up window or save to a png file.

        This method uses the Cairo graphics library to plot the data read from
        the transplace file. The plot can be saved to a png file if a file name
        is provided. Otherwise, a default file name `CairoPlot.DEFAULT_PNG_NAME`
        is used.

        Args:
            png_name: Name of the png file to save the plot. If None, a default
              name `CairoPlot.DEFAULT_PNG_NAME` is used.
        """
        print('[CairoPlot] Plotting data using Cairo')

        # Create a plot.
        print('[CairoPlot] Creating plot...')
        surface_width, surface_height = 2000, 2000
        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, surface_width, surface_height)
        context = cairo.Context(surface)

        # Set the background color (optional, to fill the canvas)
        context.set_source_rgb(1, 1, 1)  # White background
        context.paint()

        # Move origin to bottom-left corner and flip the y-axis (scale by -1)
        context.translate(0, surface_height)
        context.scale(1, -1)

        die_xl, die_yl, die_xh, die_yh = self._get_die_area()
        die_width, die_height = die_xh - die_xl, die_yh - die_yl

        x_low, y_low, x_high, y_high = self._get_plot_boundary()
        actual_width, actual_height = x_high - x_low, y_high - y_low

        # Set the scale and translate the origin.
        scale_x = surface_width / actual_width
        scale_y = surface_height / actual_height
        scale_factor = min(scale_x, scale_y)
        context.scale(scale_factor, scale_factor)

        # Shift to the center of the surface. Use the actual width and height.
        context.translate((surface_width / scale_factor - die_width) / 2,
                          (surface_height / scale_factor - die_height) / 2)

        # Adjust the linewidth based on the scale factor. Because the linewidth
        # will be scaled down by the same factor as the coordinates, we need to
        # scale it back up to maintain the same visual appearance.
        self._adjust_linewidth(scale_factor)

        # Note(ChenHaoHSU): The order is important.
        # Adjust (self._adjust_linewidth) the linewidth first, then generate the
        # objects. Otherwise, the linewidth will not be scaled correctly.

        # Generate rectangles for rows.
        print('[CairoPlot] Generating row rectangles...')
        row_rectangles = self._generate_row_rectangles()

        # Generate rectangles for transistors.
        print('[CairoPlot] Generating transistor rectangles...')
        transistor_rectangles = self._generate_transistor_rectangles()

        # Draw the objects.
        for obj in row_rectangles:
            obj.draw(context)
        for obj in transistor_rectangles:
            obj.draw(context)

        # Make sure the png_name is not None.
        if png_name is None:
            png_name = CairoPlot.DEFAULT_PNG_NAME
            print(f'[CairoPlot] No PNG file name specified. '
                  f'Saving to \'{png_name}\'...')

        # Save the image to a png file
        surface.write_to_png(png_name)
        print(f'[CairoPlot] Image saved to \'{png_name}\'.')
