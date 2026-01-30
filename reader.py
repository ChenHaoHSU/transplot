"""Reader of the transplot file with syntax version1 or version2."""

import copy
import json
import re
from typing import Any, Dict, List, Tuple, Union


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
        self._parsing_transistors_flag: bool = False

        # Number of transistors.
        self._num_transistors: int = 0

        # Verbose flag.
        self._verbose: bool = False

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
        self._parsing_transistors_flag = False
        self._num_transistors = 0

        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    self._parse_line(line)
        except FileNotFoundError:
            if self._verbose:
                print(f'[ReaderV1] Error: The file "{path}" was not found.')
            return False
        except (ValueError, IndexError) as e:
            if self._verbose:
                print(f'[ReaderV1] Error: {e}')
            return False

        return True

    def _parse_line(self, line: str) -> None:
        """Parses a line from the file."""
        if self._parsing_transistors_flag:
            if len(self.data['transistors']) >= self._num_transistors:
                if line.startswith('END TRANSISTORS'):
                    self._parsing_transistors_flag = False
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
                self._parsing_transistors_flag = True
                self._num_transistors = self._parse_int(line)
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
            'ports': [],
            'transistors': [],
            'pins': [],
            'sdcs': [],
            'sdc_group': {},
            'transistor_offset': None,
            'paths': [],
        }

        self._verbose: bool = False

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
            if self._verbose:
                print(f'[ReaderV2] Error: The file "{path}" was not found.')
            return False
        except (ValueError, IndexError) as e:
            if self._verbose:
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
            elif line.startswith('PORT'):
                port_info = self._parse_port(line)
                self.data['ports'].append(port_info)
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

    def _parse_port(self, line: str) -> Dict[str, Union[int, str]]:
        """Parses a PORT line."""
        tokens = line.split()
        if len(tokens) != 7:
            raise IndexError(
                f'Expect 7 fields but found {len(tokens)} fields.')
        t = {
            'name': tokens[1],
            'net_name': tokens[2],
            'x': int(tokens[3]),
            'y': int(tokens[4]),
            'width': int(tokens[5]),
            'height': int(tokens[6]),
        }

        return t

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
        edges = re.findall(r'\(\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\)', line)

        p = [((int(x1), int(y1)), (int(x2), int(y2)))
             for x1, y1, x2, y2 in edges]

        print(p)

        return p


class ReaderJson:
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
            'transistor_offset': None,
            'ports': [],
            'transistors': [],
            'pins': [],
            'sdcs': [],
            'sdc_group': {},
            'paths': [],
        }

        self._verbose: bool = False

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
            with open(path, "r") as f:
                json_data = json.load(f)
                self.data['die_area'] = self._get_die_area(json_data)
                self.data['row_height'] = self._get_row_height(json_data)
                self.data['site_width'] = self._get_site_width(json_data)
                self.data['num_rows'] = self._get_num_rows(json_data)
                self.data['num_sites'] = self._get_num_sites(json_data)
                self.data['ports'] = self._get_ports(json_data)
                self.data['transistors'] = self._get_transistors(json_data)
                self.data['pins'] = self._get_pins(json_data)
                self.data['sdcs'] = self._get_sdcs(json_data)
                self.data['paths'] = self._get_paths(json_data)
        except FileNotFoundError:
            if self._verbose:
                print(f'[ReaderJson] Error: The file "{path}" was not found.')
            return False
        except (ValueError, IndexError) as e:
            if self._verbose:
                print(f'[ReaderJson] Error: {e}')
            return False

        return True

    def _get_die_area(self, json_data: Dict[str, Any]) -> Tuple[int]:
        """Gets the die area from the JSON data."""
        die_area_json = json_data.get('canvas', {}).get('die_area', None)
        if die_area_json is None:
            raise ValueError('[ReaderJson] Die area not found in JSON data.')
        xl = die_area_json.get('xl', None)
        yl = die_area_json.get('yl', None)
        xh = die_area_json.get('xh', None)
        yh = die_area_json.get('yh', None)
        if None in (xl, yl, xh, yh):
            raise ValueError(
                '[ReaderJson] Die area is incomplete in JSON data.')
        return (xl, yl, xh, yh)

    def _get_row_height(self, json_data: Dict[str, Any]) -> int:
        """Gets the row height from the JSON data."""
        row_height = json_data.get('canvas', {}).get('row_height', None)
        if row_height is None:
            raise ValueError('[ReaderJson] Row height not found in JSON data.')
        return row_height

    def _get_site_width(self, json_data: Dict[str, Any]) -> int:
        """Gets the site width from the JSON data."""
        site_width = json_data.get('canvas', {}).get('site_width', None)
        if site_width is None:
            raise ValueError('[ReaderJson] Site width not found in JSON data.')
        return site_width

    def _get_num_rows(self, json_data: Dict[str, Any]) -> int:
        """Gets the number of rows from the JSON data."""
        num_rows = json_data.get('canvas', {}).get('rows', None)
        if num_rows is None:
            raise ValueError(
                '[ReaderJson] Number of rows not found in JSON data.')
        return num_rows

    def _get_num_sites(self, json_data: Dict[str, Any]) -> int:
        """Gets the number of sites from the JSON data."""
        num_sites = json_data.get('canvas', {}).get('sites', None)
        if num_sites is None:
            raise ValueError(
                '[ReaderJson] Number of sites not found in JSON data.')
        return num_sites

    def _get_ports(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gets the ports from the JSON data."""
        ports_json = json_data.get('ports', [])
        ports = []
        for port_json in ports_json:
            port = {
                'name': port_json.get('name', ''),
                'net_name': port_json.get('net_name', ''),
                'x': port_json.get('x', 0),
                'y': port_json.get('y', 0),
                'width': port_json.get('width', 0),
                'height': port_json.get('height', 0),
            }
            ports.append(port)
        return ports

    def _get_transistors(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gets the transistors from the JSON data."""
        transistors_json = json_data.get('transistors', [])
        transistors = []
        sdc_group = {}
        for transistor_json in transistors_json:
            t = {
                'name': transistor_json.get('name', ''),
                'x': transistor_json.get('x', 0),
                'y': transistor_json.get('y', 0),
                'flipped': transistor_json.get('flipped', 0),
                'type': transistor_json.get('type', ''),
                'sdc': transistor_json.get('sdc', ''),
            }

            # Update SDC group count.
            transistors.append(t)
            sdc = t['sdc']
            if sdc not in sdc_group:
                sdc_group[sdc] = 1
            else:
                sdc_group[sdc] += 1

        self.data['sdc_group'] = sdc_group
        return transistors

    def _get_pins(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gets the pins from the JSON data."""
        pins_json = json_data.get('pins', [])
        pins = []
        for pin_json in pins_json:
            pin = {
                'name': pin_json.get('name', ''),
                'net_name': pin_json.get('net_name', ''),
                'x': pin_json.get('x', 0),
                'y': pin_json.get('y', 0),
            }
            pins.append(pin)
        return pins

    def _get_sdcs(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gets the sdcs from the JSON data."""
        sdcs_json = json_data.get('sdcs', [])
        sdcs = []
        for sdc_json in sdcs_json:
            sdc = {
                'name': sdc_json.get('name', ''),
                'macro': sdc_json.get('macro', ''),
                'x': sdc_json.get('x', 0),
                'y': sdc_json.get('y', 0),
                'width': sdc_json.get('width', 0),
                'height': sdc_json.get('height', 0),
            }
            sdcs.append(sdc)
        return sdcs

    def _get_paths(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gets the paths from the JSON data."""
        paths_json = json_data.get('paths', [])
        paths = []
        for path_json in paths_json:
            edges_json = path_json.get('edges', [])
            edges = []
            for edge_json in edges_json:
                from_node = edge_json.get('from_node', {})
                to_node = edge_json.get('to_node', {})
                x1 = from_node.get('x', 0)
                y1 = from_node.get('y', 0)
                x2 = to_node.get('x', 0)
                y2 = to_node.get('y', 0)
                edges.append(((x1, y1), (x2, y2)))
            paths.append(edges)
        return paths
