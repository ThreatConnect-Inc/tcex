"""TcEx Utilities Module"""
# standard library
import ipaddress
import re
from typing import Any, List, Optional, Union

# third-party
import jmespath

# first-party
from tcex.utils.aes_operations import AesOperations
from tcex.utils.datetime_operations import DatetimeOperations
from tcex.utils.string_operations import StringOperations


class Utils(AesOperations, DatetimeOperations, StringOperations):
    """TcEx Utilities Class"""

    @staticmethod
    def flatten_list(lst: List[Any]) -> List[Any]:
        """Flatten a list

        Will work for lists of lists to arbitrary depth
        and for lists with a mix of lists and single values
        """
        flat_list = []
        for sublist in lst:
            if isinstance(sublist, list):
                for item in Utils.flatten_list(sublist):
                    flat_list.append(item)
            else:
                flat_list.append(sublist)
        return flat_list

    @staticmethod
    def is_cidr(possible_cidr_range: str) -> bool:
        """Return True if the provided value is a valid CIDR block.

        Args:
            possible_cidr_range: The cidr value to validate.
        """
        try:
            ipaddress.ip_address(possible_cidr_range)
        except ValueError:
            try:
                ipaddress.ip_interface(possible_cidr_range)
            except Exception:
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def is_ip(possible_ip: str) -> bool:
        """Return True if the provided value is a valid IP address.

        Args:
            possible_ip: The IP value to validate.
        """
        try:
            ipaddress.ip_address(possible_ip)
        except ValueError:
            return False
        else:
            return True

    def mapper(self, data: Union[list, dict], mapping: dict):
        """Yield something ..."""
        # TODO [high] - @bpurdy - update docstring with description of what this is?
        if isinstance(data, dict):
            data = [data]
        try:
            for d in data:
                mapped_obj = mapping.copy()
                for key, value in mapping.items():
                    if isinstance(value, list):
                        new_list = []
                        for item in value:
                            if isinstance(item, dict):
                                new_list.append(list(self.mapper(d, item))[0])
                            else:
                                if not item.startswith('@'):
                                    new_list.append(item)
                                else:
                                    new_list.append(
                                        jmespath.search(f'{item}', jmespath.search('@', d))
                                    )

                        mapped_obj[key] = new_list
                    elif isinstance(value, dict):
                        mapped_obj[key] = list(self.mapper(d, mapped_obj[key]))[0]
                    else:
                        if not value.startswith('@'):
                            mapped_obj[key] = value
                        else:
                            mapped_obj[key] = jmespath.search(f'{value}', jmespath.search('@', d))
                yield mapped_obj
        except Exception:  # nosec
            pass

    @staticmethod
    def printable_cred(
        cred: str,
        visible: Optional[int] = 1,
        mask_char: Optional[str] = '*',
        mask_char_count: Optional[int] = 4,
    ) -> str:
        """Return a printable (masked) version of the provided credential.

        Args:
            cred: The cred to print.
            visible: The number of characters at the beginning and ending of the cred to not mask.
            mask_char: The character to use in the mask.
            mask_char_count: How many mask character to insert (obscure cred length).
        """
        if isinstance(cred, str):
            mask_char = mask_char or '*'
            if cred is not None and len(cred) >= visible * 2:
                cred = f'{cred[:visible]}{mask_char * mask_char_count}{cred[-visible:]}'
        return cred

    @staticmethod
    def standardize_asn(asn: str) -> str:
        """Return the ASN formatted for ThreatConnect.

        Args:
            asn: The asn value to standardize.
        """
        numbers = re.findall('[0-9]+', asn)
        if len(numbers) == 1:
            asn = f'ASN{numbers[0]}'
        return asn

    @property
    def variable_match(self) -> Any:
        """Return compiled re pattern."""
        return re.compile(fr'^{self.variable_pattern}$')

    def variable_method_name(self, variable: str) -> str:
        """Convert variable name to a valid method name.

        #App:9876:string.operation!String -> string_operation_string

        Args:
            variable: The variable name to convert.
        """
        method_name = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self.variable_match, variable):
                var = re.search(self.variable_parse, variable)
                variable_name = var.group(3).replace('.', '_').lower()
                variable_type = var.group(4).lower()
                method_name = f'{variable_name}_{variable_type}'
        return method_name

    @property
    def variable_parse(self) -> Any:
        """Return compiled re pattern."""
        return re.compile(self.variable_pattern)

    @property
    def variable_pattern(self) -> str:
        """Regex pattern to match and parse a playbook variable."""
        return (
            r'#([A-Za-z]+)'  # match literal (#App) at beginning of String
            r':([\d]+)'  # app id (:7979)
            r':([A-Za-z0-9_\.\-\[\]]+)'  # variable name (:variable_name)
            r'!(StringArray|BinaryArray|KeyValueArray'  # variable type (array)
            r'|TCEntityArray|TCEnhancedEntityArray'  # variable type (array)
            r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'  # variable type
            r'|(?:(?!String)(?!Binary)(?!KeyValue)'  # non matching for custom
            r'(?!TCEntity)(?!TCEnhancedEntity)'  # non matching for custom
            r'[A-Za-z0-9_-]+))'  # variable type (custom)
        )
