"""
Transplot is a Python package for plotting and visualizing transistor placement.
"""
from typing import Any, List, Dict, Union, Tuple
import cairo


class PlotRectangle:
    """
    A class to represent a plot object (rectangle) with fill and stroke RGBA colors.
    """

    def __init__(self, x: int, y: int, w: int, h: int,
                 fill: bool = True,
                 fill_rgba: Tuple[float, float, float, float] = (1, 1, 1, 1),
                 stroke: bool = False,
                 stroke_rgba: Tuple[float, float, float, float] = (0, 0, 0, 1),
                 line_width: int = 1):
        """
        Initialize the PlotRectangle object.

        @param x: x-coordinate of the top-left corner of the rectangle
        @param y: y-coordinate of the top-left corner of the rectangle
        @param w: Width of the rectangle
        @param h: Height of the rectangle
        @param fill: Whether to fill the rectangle (default is True)
        @param fill_rgba: Fill color of the rectangle (R, G, B, A)
        @param stroke: Whether to outline the rectangle (default is False)
        @param stroke_rgba: Stroke color of the rectangle (R, G, B, A)
        @param line_width: Width of the stroke line (default is 1)
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.fill_rgba = fill_rgba
        self.stroke_rgba = stroke_rgba
        self.line_width = line_width
        self.fill = fill
        self.stroke = stroke

    def __repr__(self):
        return f'PlotRectangle(x={self.x}, y={self.y}, w={self.w}, ' \
               f'h={self.h}, fill={self.fill}, stroke={self.stroke})'

    def draw(self, context: cairo.Context):
        """
        Draw the rectangle on the given Cairo context with specified RGBA colors.

        @param context: A Cairo context to draw the rectangle on.
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
            context.set_line_width(self.line_width)
            context.rectangle(self.x, self.y, self.w, self.h)
            context.stroke()


class Transplot:
    """
    A class to read and visualize transistor placement data.
    """

    def __init__(self):
        self.params: Dict[str, Any] = {
            'scale': 50,
            'row_stroke_rgba': (0, 0, 0, 1),
            'row_linewidth': 1.0,
            'transistor_width': 1728,
            'transistor_height': 3456,
            'transistor_stroke_rgba': (0, 0, 0, 1),
            'transistor_linewidth': 0.8,
            'transistor_alpha': {'NMOS': 0.9, 'PMOS': 0.5},
            'transistor_alpha_inv': {'NMOS': 0.4, 'PMOS': 0.25},
            'transistor_poly_shrink_ratio': 0.2,
            'transistor_diffusion_shrink_ratio': 0.5,
        }
        self.data: Dict[str, Any] = {
            'units': None,
            'die_area': None,
            'row_height': None,
            'site_width': None,
            'num_rows': None,
            'num_sites': None,
            'transistors': [],
            'sdc_group': {},
        }
        # TODO(ChenHaoHSU): Add more colors.
        self.colors = [
            (0., 0., 1.),
            (1., 0., 0.),
            (0., 0.5, 0.),
            (0.647, 0.165, 0.165),
            (0.933, 0.51, 0.933),
            (1., 1., 0.),
            (0., 0., 0.),
            (0.5, 0.5, 0.),
            (1., 1., 0.941),
            (1., 0.647, 0.),
            (1., 0.753, 0.796),
            (0., 1., 1.),
            (0.824, 0.412, 0.118),
            (0.118, 0.565, 1.),
            (0., 1., 0.),
            (0.392, 0.584, 0.929),
            (0.294, 0., 0.51),
            (0.5, 0., 0.5),
            (0.824, 0.706, 0.549),
            (0.18, 0.545, 0.341)]

    def read(self, filepath: str) -> None:
        """
        Read the data from a file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    self._parse_line(line)
        except FileNotFoundError:
            print(f'Error: The file "{filepath}" was not found.')

    def _parse_line(self, line: str) -> None:
        try:
            if line.startswith('UNITS'):
                self.data['units'] = self._parse_int(line)
            elif line.startswith('DIEAREA'):
                self.data['die_area'] = self._parse_diearea(line)
            elif line.startswith('ROWHEIGHT'):
                self.data['row_height'] = self._parse_int(line)
            elif line.startswith('SITEWIDTH'):
                self.data['site_width'] = self._parse_int(line)
            elif line.startswith('ROWS'):
                self.data['num_rows'] = self._parse_int(line)
            elif line.startswith('SITES'):
                self.data['num_sites'] = self._parse_int(line)
            elif line.startswith('TRANSISTOR'):
                transistor_info = self._parse_transistor(line)
                self.data['transistors'].append(transistor_info)
        except ValueError as ve:
            print(f"Value error when parsing line '{line}': {ve}")
        except IndexError as ie:
            print(
                f"Index error: Possibly missing fields in line '{line}': {ie}")

    def _parse_int(self, line: str) -> int:
        return int(line.split()[1])

    def _parse_diearea(self, line: str) -> Tuple[int]:
        tokens = tuple(map(int, line.split()[1:]))
        if len(tokens) != 4:
            raise ValueError(
                f'DIEAREA should have exactly 4 values, but found: {len(tokens)}')
        return tokens

    def _parse_transistor(self, line: str) -> Dict[str, Union[int, str]]:
        tokens = line.split()
        if len(tokens) < 7:
            raise IndexError(
                'TRANSISTOR line does not have enough fields.')
        t = {
            'name': tokens[1],
            'x': int(tokens[2]),
            'y': int(tokens[3]),
            'flipped': int(tokens[4]),
            'type': tokens[5],
            'sdc': int(tokens[6])
        }

        # Update SDC group count.
        if t['sdc'] not in self.data['sdc_group']:
            self.data['sdc_group'][t['sdc']] = 1
        else:
            self.data['sdc_group'][t['sdc']] += 1

        return t

    def get_data(self) -> Dict[str, Any]:
        """
        Get the data read from the file.
        """
        return self.data

    def generate_row_rectangles(self) -> List[PlotRectangle]:
        """
        Generate plot rectangles for rows.
        """
        if not self.data['die_area'] or not self.data['row_height']:
            return []

        die_xl, die_yl, die_xh, _ = tuple(self.data['die_area'])

        scale = self.params['scale']

        row_start_x = die_xl / scale
        row_start_y = die_yl / scale
        row_width = (die_xh - die_xl) / scale
        row_height = self.data['row_height'] / scale

        def gen_rect(i: int) -> PlotRectangle:
            return PlotRectangle(x=row_start_x, y=row_start_y + i * row_height,
                                 w=row_width, h=row_height,
                                 fill=False,
                                 stroke=True,
                                 stroke_rgba=self.params['row_stroke_rgba'],
                                 line_width=self.params['row_linewidth'])

        rectangles = []
        for i in range(self.data['num_rows']):
            rectangles.append(gen_rect(i))

        return rectangles

    def generate_transistor_rectangles(self) -> List[PlotRectangle]:
        """
        Generate plot rectangles for transistors.
        """

        scale = self.params['scale']
        tran_width = self.params['transistor_width'] / scale
        tran_height = self.params['transistor_height'] / scale

        def gen_rect(
                transistor: Dict[str, Any]) -> List[PlotRectangle]:
            tran_x = transistor['x'] / scale
            tran_y = transistor['y'] / scale

            # Fill.
            # Inverter: black. Others: random color.
            tran_type = transistor['type']
            fill_rgb, fill_alpha = (0, 0, 0), 1.0
            if self.data['sdc_group'][transistor['sdc']] <= 2:
                fill_rgb = (0.03, 0.03, 0.03)
                fill_alpha = self.params['transistor_alpha_inv'][tran_type]
            else:
                fill_rgb = self.colors[transistor['sdc'] % len(self.colors)]
                fill_alpha = self.params['transistor_alpha'][tran_type]
            fill_rgba = fill_rgb + (fill_alpha,)

            # Diffusion rectangle.
            diff_shrink_ratio = self.params['transistor_diffusion_shrink_ratio']
            diff_y = tran_y + (tran_height * (1 - diff_shrink_ratio) / 2)
            diff_height = tran_height * diff_shrink_ratio
            diffusion_rect = PlotRectangle(
                x=tran_x, y=diff_y, w=tran_width, h=diff_height,
                fill=True, fill_rgba=fill_rgba,
                stroke=True, stroke_rgba=self.params['transistor_stroke_rgba'],
                line_width=self.params['transistor_linewidth'])

            # Poly rectangle.
            poly_shrink_ratio = self.params['transistor_poly_shrink_ratio']
            poly_x = tran_x + (tran_width * (1 - poly_shrink_ratio) / 2)
            poly_width = tran_width * poly_shrink_ratio
            poly_rect = PlotRectangle(
                x=poly_x, y=tran_y, w=poly_width, h=tran_height,
                fill=True, fill_rgba=fill_rgba,
                stroke=True, stroke_rgba=self.params['transistor_stroke_rgba'],
                line_width=self.params['transistor_linewidth'])

            return [diffusion_rect, poly_rect]

        rectangles = []
        for transistor in self.data['transistors']:
            rectangles.extend(gen_rect(transistor))

        return rectangles

    def plot(self, png_name: str = 'test.png') -> None:
        """
        Plot the data to a pop-up window or save to a png file.
        """
        # Generate rectangles for rows.
        print("Generating row rectangles...")
        row_rectangles = self.generate_row_rectangles()
        # Generate rectangles for transistors.
        print("Generating transistor rectangles...")
        transistor_rectangles = self.generate_transistor_rectangles()

        # Create a plot.
        print("Creating plot...")
        width, height = 1000, 1000
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)

        # Set the background color (optional, to fill the canvas)
        context.set_source_rgb(1, 1, 1)  # White background
        context.paint()

        # Draw the objects.
        for obj in row_rectangles:
            obj.draw(context)
        for obj in transistor_rectangles:
            obj.draw(context)

        # Save the image to a png file
        surface.write_to_png(png_name)
        print(f"Image saved to '{png_name}'.")
