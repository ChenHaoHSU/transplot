"""Base class for all plot classes."""

from typing import Any, Dict, Tuple, Union


class BasePlot:
    """Base class for all plot classes.

    This class defines the common interface for all plot classes. It also
    provides a common data structure to store the data read from the input file.
    """

    def __init__(self):
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
            (0, 0, 255),  # Blue
            (255, 0, 0),  # Red
            (0, 128, 0),  # Green
            (165, 42, 42),  # Brown
            (238, 130, 238),  # Violet
            (255, 255, 0),  # Yellow
            (0, 0, 0),  # Black
            (128, 128, 0),  # Olive
            (255, 255, 240),  # Ivory
            (255, 165, 0),  # Orange
            (255, 192, 203),    # Pink
            (0, 255, 255),  # Aqua
            (210, 105, 30),  # Chocolate
            (30, 144, 255),  # DodgerBlue
            (0, 255, 0),   # Lime
            (100, 149, 237),  # CornflowerBlue
            (75, 0, 130),  # Indigo
            (128, 0, 128),  # Purple
            (210, 180, 140),  # Tan
            (46, 139, 87),  # SeaGreen
        ]

    def read(self, path: str) -> None:
        """Reads the data from a file.

        Args:
            path: The file path.
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    self._parse_line(line)
        except FileNotFoundError:
            print(f'Error: The file "{path}" was not found.')

    def _parse_line(self, line: str) -> None:
        """Parses a line from the file."""
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
        """Parses an integer from a line with the format 'KEY VALUE'."""
        return int(line.split()[1])

    def _parse_diearea(self, line: str) -> Tuple[int]:
        """Parses the DIEAREA line."""
        tokens = tuple(map(int, line.split()[1:]))
        if len(tokens) != 4:
            raise ValueError(
                f'DIEAREA should have exactly 4 values, but found: {len(tokens)}')
        return tokens

    def _parse_transistor(self, line: str) -> Dict[str, Union[int, str]]:
        """Parses a TRANSISTOR line."""
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

    def _convert_int_to_float_rgb(self, rgb: Tuple[int, int, int]) -> Tuple[
            float, float, float]:
        """Converts an integer RGB tuple to a float RGB tuple.

        Args:
            rgb: An integer RGB tuple.

        Returns:
            A float RGB tuple.
        """
        return tuple(map(lambda x: x / 255., rgb))

    def get_data(self) -> Dict[str, Any]:
        """Gets the data read from the file.

        Returns:
            The data read from the file.
        """
        return self.data

    def plot(self):
        """Plots the data.

        This method should be implemented by child classes.
        """
        raise NotImplementedError
