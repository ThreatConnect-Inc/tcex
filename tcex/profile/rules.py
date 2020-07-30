# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
# import json
# standard library
import json
import re

# third-party
import colorama as c

# autoreset colorama
c.init(autoreset=True, strip=False)


class Rules:
    """Class for profile Migration methods management."""

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

    def data(self, data: str) -> dict:  # pylint: disable=too-many-return-statements
        """Return the default output data for a given variable

        Args:
            data (any): The output data from the App for the current variable.

        Returns:
            []: [description]
        """

        # NOTE: The order of these if statements matter.
        if data is None:
            return {'expected_output': data, 'op': 'eq'}
        if self.matches_url_rule(data):
            return {'expected_output': data, 'op': 'is_url'}
        if self.matches_number_rule(data):
            return {'expected_output': data, 'op': 'is_number'}
        if self.matches_jeq_rule(data):
            return {
                'expected_output': data,
                'op': 'jeq',
                'ignore_order': False,
                'exclude_paths': [],
            }
        if self.matches_date_rule(data):
            return {'expected_output': data, 'op': 'is_date'}
        if self.matches_dd_rule(data):
            return {'expected_output': data, 'op': 'dd', 'ignore_order': False, 'exclude_paths': []}
        return {'expected_output': data, 'op': 'eq'}

    @staticmethod
    def matches_number_rule(outputs):
        """Return if output should use the is_number operator."""
        if not isinstance(outputs, list):
            outputs = [outputs]
        try:
            for output in outputs:
                int(output)
        except Exception:
            return False
        return True

    @staticmethod
    def matches_url_rule(outputs):
        """Return if output should use the is_url operator."""
        if not isinstance(outputs, list):
            outputs = [outputs]

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE,
        )
        try:
            for output in outputs:
                matched = re.match(regex, output)
                if not matched:
                    return False
        except Exception:
            return False
        return True

    def matches_date_rule(self, outputs):
        """Return if output should use the is_date operator."""
        if not isinstance(outputs, list):
            outputs = [outputs]

        for output in outputs:
            # date_to_datatime will take int/floats and convert to date.
            # if the value can be converted to int/float then it will
            # not be considered a date for this rule.
            try:
                is_float = True
                float(output)
            except Exception:
                is_float = False
            else:
                if is_float:
                    return False

            try:
                is_int = True
                int(output)
            except Exception:
                is_int = False
            else:
                if is_int:
                    return False

            try:
                if self.profile.utils.datetime.date_to_datetime(output) is None:
                    return False
            except RuntimeError:
                return False

        return True

    @staticmethod
    def matches_jeq_rule(outputs):
        """Return if output should use the jeq operator."""
        # TODO: APP-674 - revisit this with Ben
        if not isinstance(outputs, list):
            outputs = [outputs]
        try:
            for output in outputs:
                if not isinstance(output, str):
                    return False
                if not isinstance(json.loads(output), (dict, list)):
                    return False
        except Exception:
            return False
        return True

    @staticmethod
    def matches_dd_rule(outputs):
        """Return if output should use the dd operator."""
        return isinstance(outputs, (dict, list))
