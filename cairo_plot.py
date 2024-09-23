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
               f''

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

    def __init__(self):
        super().__init__()
        self.params: Dict[str, Any] = {
            # Scale factor for the plot.
            'scale': 50,
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

    def generate_row_rectangles(self) -> List[CairoRect]:
        """Generates plot rectangles for rows.

        Returns:
            A list of CairoRect objects representing rows.
        """
        if not self.data['die_area'] or not self.data['row_height']:
            return []

        die_xl, die_yl, die_xh, _ = tuple(self.data['die_area'])

        scale = self.params['scale']

        row_start_x = die_xl / scale
        row_start_y = die_yl / scale
        row_width = (die_xh - die_xl) / scale
        row_height = self.data['row_height'] / scale

        def gen_rect(i: int) -> CairoRect:
            return CairoRect(x=row_start_x, y=row_start_y + i * row_height,
                             w=row_width, h=row_height,
                             fill=False,
                             stroke=True,
                             stroke_rgba=self.params['row_stroke_rgba'],
                             linewidth=self.params['row_linewidth'])

        rectangles = []
        for i in range(self.data['num_rows']):
            rectangles.append(gen_rect(i))

        return rectangles

    def generate_transistor_rectangles(self) -> List[CairoRect]:
        """Generates plot rectangles for transistors.

        Returns:
            A list of CairoRect objects representing transistors.
        """
        scale = self.params['scale']
        tran_width = self.params['transistor_width'] / scale
        tran_height = self.params['transistor_height'] / scale

        def gen_rect(
                transistor: Dict[str, Any]) -> List[CairoRect]:
            # Transistor location (scaled).
            tran_x = transistor['x'] / scale
            tran_y = transistor['y'] / scale

            # Fill.
            # Inverter: black. Others: random color.
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
            fill_rgba = fill_rgb + (fill_alpha,)

            # Stroke.
            stroke_rgb = self._convert_int_to_float_rgb(
                self.params['transistor_stroke_rgb'])
            stroke_rgba = stroke_rgb + (self.params['transistor_stroke_alpha'],)
            linewidth = self.params['transistor_linewidth']

            # Diffusion rectangle.
            diff_shrink_ratio = self.params['transistor_diffusion_shrink_ratio']
            diff_y = tran_y + (tran_height * (1 - diff_shrink_ratio) / 2)
            diff_height = tran_height * diff_shrink_ratio
            diffusion_rect = CairoRect(
                x=tran_x, y=diff_y, w=tran_width, h=diff_height, fill=True,
                fill_rgba=fill_rgba, stroke=True, stroke_rgba=stroke_rgba,
                linewidth=linewidth)

            # Poly rectangle.
            poly_shrink_ratio = self.params['transistor_poly_shrink_ratio']
            poly_x = tran_x + (tran_width * (1 - poly_shrink_ratio) / 2)
            poly_width = tran_width * poly_shrink_ratio
            poly_rect = CairoRect(
                x=poly_x, y=tran_y, w=poly_width, h=tran_height, fill=True,
                fill_rgba=fill_rgba, stroke=True, stroke_rgba=stroke_rgba,
                linewidth=linewidth)

            return [diffusion_rect, poly_rect]

        rectangles = []
        for transistor in self.data['transistors']:
            rectangles.extend(gen_rect(transistor))

        return rectangles

    def plot(self, png_name: str = None) -> None:
        """Plots the data to a pop-up window or save to a png file.

        This method uses the Cairo graphics library to plot the data read from
        the transplace file. The plot can be saved to a png file if a file name
        is provided. Otherwise, a default file name 'cairo_plot.png' is used.

        Args:
            png_name: Name of the png file to save the plot. If None, a default
              name 'cairo_plot.png' is used.
        """
        print('[CairoPlot] Plotting data using Cairo')

        # Generate rectangles for rows.
        print('[CairoPlot] Generating row rectangles...')
        row_rectangles = self.generate_row_rectangles()

        # Generate rectangles for transistors.
        print('[CairoPlot] Generating transistor rectangles...')
        transistor_rectangles = self.generate_transistor_rectangles()

        # Create a plot.
        print('[CairoPlot] Creating plot...')
        width, height = 1000, 1000
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)

        # Set the background color (optional, to fill the canvas)
        context.set_source_rgb(1, 1, 1)  # White background
        context.paint()

        # Flip the y-axis (scale by -1 and move origin) to match the plot.
        context.translate(0, height)  # Move origin to bottom-left corner
        context.scale(1, -1)  # Flip y-axis

        # Draw the objects.
        for obj in row_rectangles:
            obj.draw(context)
        for obj in transistor_rectangles:
            obj.draw(context)

        # Save the image to a png file
        if png_name is None:
            png_name = 'cairo_plot.png'
            print(f'[CairoPlot] No PNG file name specified. '
                  f'Saving to \'{png_name}\'...')
        surface.write_to_png(png_name)
        print(f'[CairoPlot] Image saved to \'{png_name}\'.')
