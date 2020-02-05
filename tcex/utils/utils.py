# -*- coding: utf-8 -*-
"""TcEx Utilities Module"""
import os
import random
import re
import string
import uuid

from typing import List, Any

from .date_utils import DatetimeUtils


class Utils:
    """TcEx framework Utils Class

    Args:
        tcex (object): Instance of TcEx.
    """

    def __init__(self, tcex=None):
        """Initialize the Class properties."""
        self.tcex = tcex

        # properties
        self._camel_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        self._inflect = None

    def camel_to_snake(self, camel_string):
        """Return snake case string from a camel case string.

        Args:
            camel_string (str): The camel case input string.

        Returns:
            str: The snake case representation of input string.
        """
        return self._camel_pattern.sub('_', camel_string).lower()

    def camel_to_space(self, camel_string):
        """Return space case string from a camel case string.

        Args:
            camel_string (str): The camel case input string.

        Returns:
            str: The space representation of input string.
        """
        return self._camel_pattern.sub(' ', camel_string).lower()

    @property
    def datetime(self):
        """Return an instance of DatetimeUtils."""
        return DatetimeUtils()

    @property
    def inflect(self):
        """Return instance of inflect."""
        if self._inflect is None:
            import inflect

            self._inflect = inflect.engine()
        return self._inflect

    @staticmethod
    def random_string(string_length=10):
        """Generate a random string of fixed length

        Args:
            string_length (int, optional): The length of the string. Defaults to 10.

        Returns:
            str: A random string
        """
        return ''.join(random.choice(string.ascii_letters) for i in range(string_length))

    @staticmethod
    def snake_to_camel(snake_string):
        """Convert snake_case to camelCase

        Args:
            snake_string (str): The snake case input string.
        """
        components = snake_string.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def write_temp_binary_file(self, content, filename=None):
        """Write content to a temporary file.

        Args:
            content (bytes): The file content.
            filename (str, optional): The filename to use when writing the file.

        Returns:
            str: Fully qualified path name for the file.

        """
        return self.write_temp_file(content, filename, 'wb')

    def write_temp_file(self, content, filename=None, mode='w'):
        """Write content to a temporary file.

        If passing binary data the mode needs to be set to 'wb'.

        Args:
            content (bytes|str): The file content.
            filename (str, optional): The filename to use when writing the file. Defaults to None.
            mode (str, optional): The write mode ('w' or 'wb'). Defaults to w.

        Returns:
            str: Fully qualified path name for the file.
        """
        if filename is None:
            filename = str(uuid.uuid4())
        fqpn = os.path.join(self.tcex.default_args.tc_temp_path, filename)
        os.makedirs(os.path.dirname(fqpn), exist_ok=True)
        with open(fqpn, mode) as fh:
            fh.write(content)
        return fqpn

    @staticmethod
    def to_bool(value):
        """Convert value to bool.

        Args:
            value (bool|str): The value to convert to boolean.

        Returns:
            bool: The boolean value
        """
        return str(value).lower() in ['1', 't', 'true']

    @staticmethod
    def flatten_list(lst: List[Any]) -> List[Any]:
        """Flatten a list

        Will work for lists of lists to arbitrary depth
        and for lists with a mix of lists and single values

        Args:
            lst (list): The list to flatten

        Returns:
            list: the flattened list
        """
        flat_list = []
        for sublist in lst:
            if isinstance(sublist, list):
                for item in Utils.flatten_list(sublist):
                    flat_list.append(item)
            else:
                flat_list.append(sublist)

        return flat_list
