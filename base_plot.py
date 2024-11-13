"""Base class for all plot classes."""

import os
import random
from typing import Any, Dict, Tuple, Union, List

from reader import ReaderV1, ReaderV2


class BasePlot:
    """Base class for all plot classes.

    This class defines the common interface for all plot classes. It also
    provides a common data structure to store the data read from the input file.
    """

    PREDEFINED_COLORS = [
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

    def __init__(self):
        # Random seed.
        random.seed(0)

        # Data read from the transplace file.
        self.data: Dict[str, Any] = None

        # Predefined colors.
        self.colors: List[Tuple[int, int, int]] = self.PREDEFINED_COLORS

        # Color map for SDC groups. It will be built when reading the file.
        self.color_map: Dict[str, Tuple[int, int, int]] = None

        # Target SDCs.
        self.target_sdc: List[str] = None

        # Target transistors.
        self.target_transistors: List[str] = None

    def read(self, path: str) -> bool:
        """Reads the data from a file.

        Args:
            path: The file path.

        Returns:
            True if the file was read successfully, False otherwise.

        Raises:
            FileNotFoundError: If the file is not found.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(
                f'[BasePlot] Error: The file "{path}" was not found.')

        # Try to read the file with syntax version1.
        print(f'[BasePlot] Reading file "{path} with syntax version1...')
        reader_v1 = ReaderV1()
        if reader_v1.read(path):
            print(f'[BasePlot] Successfully read the file "{path}" with '
                  'syntax version1.')
            self.data = reader_v1.get_data()
            self._build_color_map()
            return True

        print(f'[BasePlot] Error: Failed to read the file "{path}" with '
              'syntax version1.')

        # Try to read the file with syntax version2.
        print(f'[BasePlot] Reading file "{path} with syntax version2...')
        reader_v2 = ReaderV2()
        if reader_v2.read(path):
            print(f'[BasePlot] Successfully read the file "{path}" with '
                  'syntax version2.')
            self.data = reader_v2.get_data()
            self._build_color_map()
            return True

        print(f'[BasePlot] Error: Failed to read the file "{path}" with '
              'syntax version2.')

        return False

    def _convert_int_to_float_rgb(
            self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Converts an integer RGB tuple to a float RGB tuple.

        Args:
            rgb: An integer RGB tuple.

        Returns:
            A float RGB tuple.
        """
        return tuple(map(lambda x: x / 255., rgb))

    def _generate_colors(self) -> None:
        """Generates colors for the transistors.

        The predefined colors are in the `colors` attribute. If the number of
        SDC groups with more than 2 transistors is greater than the number of
        predefined colors, this method generates additional colors and appends
        them to the `colors` attribute.
        """
        num_colors = len(self.colors)
        keys = [k for k, v in self.data['sdc_group'].items() if v > 2]
        num_groups = len(keys)

        def random_color() -> Tuple[int, int, int]:
            return (random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))

        if num_groups > num_colors:
            for _ in range(num_groups - num_colors):
                self.colors.append(random_color())

    def _build_color_map(self) -> None:
        """Builds the color map for the transistors.

        The color map is a dictionary that maps SDC group names to colors.
        The color is represented as an RGB tuple.
        The color map is stored in the `color_map` attribute.
        """
        # Generate colors if needed.
        self._generate_colors()

        # Sort the SDC groups to ensure that the color assignment is consistent.
        keys = [k for k, v in self.data['sdc_group'].items() if v > 2]
        sorted_keys = sorted(keys, key=str)

        # Assign colors to SDC groups.
        self.color_map = {}
        for i, sdc in enumerate(sorted_keys):
            self.color_map[sdc] = self.colors[i]

    def set_target_sdc(self, sdc: List[str]) -> None:
        """Sets the target SDC.

        Args:
            sdc: The target SDC.
        """
        self.target_sdc = set(sdc)

    def set_target_transistors(self, transistors: List[str]) -> None:
        """Sets the target transistors.

        Args:
            transistors: The target transistors.
        """
        self.target_transistors = set(transistors)

    def _is_transistor_to_color_plot(
            self, transistor: Dict[str, Union[int, str]]) -> bool:
        """Checks if a transistor should be plotted in color.

        Args:
            transistor: The transistor to check.

        Returns:
            True if the transistor should be plotted, False otherwise.
        """
        if self.data['sdc_group'][transistor['sdc']] <= 2:
            return False
        if self.target_sdc:
            return transistor['sdc'] in self.target_sdc
        if self.target_transistors:
            return transistor['name'] in self.target_transistors

        return True

    def plot(self):
        """Plots the data.

        This method should be implemented by child classes.
        """
        raise NotImplementedError
