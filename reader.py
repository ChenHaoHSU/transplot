"""Reader of the transplot file with syntax version1 or version2."""

import copy
import re
from typing import Any, Dict, Tuple, Union


class ReaderV1:
    """Reader of the transplot file with syntax version1.

    This is a reader for the transplot file with syntax version1. The reader
    reads the file and stores the data in a dictionary. The data can be accessed
    using the get_data method.
    """

    def __init__(self):
        """Initializes the reader."""
        self.data: Dict[str, Any] = {
            'units': None,
            'die_area': None,
            'row_height': None,
            'site_width': None,
            'num_rows': None,
            'num_sites': None,
            'transistors': [],
            'sdc_group': {},
            'transistor_offset': None,
        }

        # Parsing transistor flag.
        self.parsing_transistors_flag: bool = False

        # Number of transistors.
        self.num_transistors: int = 0

    def get_data(self) -> Dict[str, Any]:
        """Gets the data read from the file.

        Returns:
            Return a deep copy of the data to prevent unintended modifications.
        """
        return copy.deepcopy(self.data)

    def read(self, path: str) -> bool:
        """Reads the data from a file.

        Args:
            path: The file path.

        Returns:
            True if the file was read successfully, False otherwise.

        Raises:
            FileNotFoundError: If the file was not found.
            ValueError: If there is a value error when parsing the file.
            IndexError: If there is an index error when parsing the file.
        """
        # Reset flags.
        self.parsing_transistors_flag = False
        self.num_transistors = 0

        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    self._parse_line(line)
        except FileNotFoundError:
            print(f'[ReaderV1] Error: The file "{path}" was not found.')
            return False
        except (ValueError, IndexError) as e:
            print(f'[ReaderV1] Error: {e}')
            return False

        return True

    def _parse_line(self, line: str) -> None:
        """Parses a line from the file."""
        if self.parsing_transistors_flag:
            if len(self.data['transistors']) >= self.num_transistors:
                if line.startswith('END TRANSISTORS'):
                    self.parsing_transistors_flag = False
                    return  # End parsing transistors.
                raise ValueError(
                    '[ReaderV1] Expect \'END TRANSISTORS\' but not found. '
                    f'At the line \'{line}\'. Parsing stopped.')
            transistor_info = self._parse_transistor(line)
            self.data['transistors'].append(transistor_info)
            return

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
            elif line.startswith('TRANSISTOROFFSET'):
                self.data['transistor_offset'] = self._parse_int(line)
            elif line.startswith('TRANSISTORS'):
                self.parsing_transistors_flag = True
                self.num_transistors = self._parse_int(line)
            else:
                raise ValueError(f'Unknown line: \'{line}\'.')
        except ValueError as ve:
            raise ValueError(
                f'Value error when parsing line \'{line}\': {ve}') from ve
        except IndexError as ie:
            raise IndexError(
                'Index error: Possibly missing fields in '
                f'line \'{line}\': {ie}') from ie

    def _parse_int(self, line: str) -> int:
        """Parses an integer from a line with the format 'KEY VALUE'."""
        tokens = line.split()
        if len(tokens) != 2:
            raise IndexError(
                f'Expect 2 fields but found {len(tokens)} fields.')
        return int(tokens[1])

    def _parse_diearea(self, line: str) -> Tuple[int]:
        """Parses the DIEAREA line."""
        tokens = tuple(map(int, line.split()[1:]))
        if len(tokens) != 4:
            raise ValueError(
                'DIEAREA should have exactly 4 fields, '
                f'but found: {len(tokens)}')
        return tokens

    def _parse_transistor(self, line: str) -> Dict[str, Union[int, str]]:
        """Parses a TRANSISTOR line."""
        tokens = line.split()
        if len(tokens) != 6:
            raise IndexError(
                f'Expect 6 fields but found {len(tokens)} fields.')
        t = {
            'name': tokens[0],
            'x': int(tokens[1]),
            'y': int(tokens[2]),
            'flipped': int(tokens[3]),
            'type': tokens[4],
            'sdc': tokens[5],  # Note it is a str
        }

        # Update SDC group count.
        if t['sdc'] not in self.data['sdc_group']:
            self.data['sdc_group'][t['sdc']] = 1
        else:
            self.data['sdc_group'][t['sdc']] += 1

        return t


class ReaderV2:
    """Reader of the transplot file with syntax version2.

    This is a reader for the transplot file with syntax version2. The reader
    reads the file and stores the data in a dictionary. The data can be accessed
    using the get_data method.
    """

    def __init__(self):
        """Initializes the reader."""
        self.data: Dict[str, Any] = {
            'units': None,
            'die_area': None,
            'row_height': None,
            'site_width': None,
            'num_rows': None,
            'num_sites': None,
            'transistors': [],
            'pins': [],
            'sdcs': [],
            'sdc_group': {},
            'transistor_offset': None,
            'paths': [],
        }

    def get_data(self) -> Dict[str, Any]:
        """Gets the data read from the file.

        Returns:
            Return a deep copy of the data to prevent unintended modifications.
        """
        return copy.deepcopy(self.data)

    def read(self, path: str) -> bool:
        """Reads the data from a file.

        Args:
            path: The file path.

        Returns:
            True if the file was read successfully, False otherwise.

        Raises:
            FileNotFoundError: If the file was not found.
            ValueError: If there is a value error when parsing the file.
            IndexError: If there is an index error when parsing the file.
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    self._parse_line(line)
        except FileNotFoundError:
            print(f'[ReaderV2] Error: The file "{path}" was not found.')
            return False
        except (ValueError, IndexError) as e:
            print(f'[ReaderV2] Error: {e}')
            return False

        return True

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
            elif line.startswith('TRANSISTOROFFSET'):
                self.data['transistor_offset'] = self._parse_int(line)
            elif line.startswith('TRANSISTOR'):
                transistor_info = self._parse_transistor(line)
                self.data['transistors'].append(transistor_info)
            elif line.startswith('PIN'):
                pin_info = self._parse_pin(line)
                self.data['pins'].append(pin_info)
            elif line.startswith('SDC'):
                sdc_info = self._parse_sdc(line)
                self.data['sdcs'].append(sdc_info)
            elif line.startswith('PATH'):
                path_info = self._parse_path(line)
                self.data['paths'].append(path_info)
            else:
                raise ValueError(f'Unknown line: \'{line}\'.')
        except ValueError as ve:
            raise ValueError(
                f'Value error when parsing line \'{line}\': {ve}') from ve
        except IndexError as ie:
            raise IndexError(
                'Index error: Possibly missing fields in '
                f'line \'{line}\': {ie}') from ie

    def _parse_int(self, line: str) -> int:
        """Parses an integer from a line with the format 'KEY VALUE'."""
        tokens = line.split()
        if len(tokens) != 2:
            raise IndexError(
                f'Expect 2 fields but found {len(tokens)} fields.')
        return int(tokens[1])

    def _parse_diearea(self, line: str) -> Tuple[int]:
        """Parses the DIEAREA line."""
        tokens = tuple(map(int, line.split()[1:]))
        if len(tokens) != 4:
            raise ValueError(
                'DIEAREA should have exactly 4 values, '
                f'but found: {len(tokens)}')
        return tokens

    def _parse_transistor(self, line: str) -> Dict[str, Union[int, str]]:
        """Parses a TRANSISTOR line."""
        tokens = line.split()
        if len(tokens) != 7:
            raise IndexError(
                f'Expect 7 fields but found {len(tokens)} fields.')
        t = {
            'name': tokens[1],
            'x': int(tokens[2]),
            'y': int(tokens[3]),
            'flipped': int(tokens[4]),
            'type': tokens[5],
            'sdc': tokens[6],  # Note it is a str
        }

        # Update SDC group count.
        if t['sdc'] not in self.data['sdc_group']:
            self.data['sdc_group'][t['sdc']] = 1
        else:
            self.data['sdc_group'][t['sdc']] += 1

        return t

    def _parse_pin(self, line: str) -> Dict[str, Union[int, str]]:
        """Parses a PIN line."""
        tokens = line.split()
        if len(tokens) != 5:
            raise IndexError(
                f'Expect 5 fields but found {len(tokens)} fields.')
        p = {
            'name': tokens[1],
            'x': int(tokens[2]),
            'y': int(tokens[3]),
            'net_name': tokens[4],
        }

        return p

    def _parse_sdc(self, line: str) -> Dict[str, Union[int, str]]:
        """Parses an SDC line."""
        tokens = line.split()
        if len(tokens) != 7:
            raise IndexError(
                f'Expect 7 fields but found {len(tokens)} fields.')
        p = {
            'name': tokens[1],
            'macro': tokens[2],
            'x': int(tokens[3]),
            'y': int(tokens[4]),
            'width': int(tokens[5]),
            'height': int(tokens[6]),
        }

        return p

    def _parse_path(self, line: str) -> Dict[str, Any]:
        """Parses a PATH line."""
        pairs = re.findall(r'\(\s*(\d+)\s+(\d+)\s*\)', line)

        p = [(int(x), int(y)) for x, y in pairs]

        return p
