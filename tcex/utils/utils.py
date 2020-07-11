# -*- coding: utf-8 -*-
"""TcEx Utilities Module"""
import ipaddress
import os
import random
import re
import string
import uuid
from typing import Any, List

import pyaes

from .date_utils import DatetimeUtils


class Utils:
    """TcEx framework Utils Class

    Args:
        temp_path (str, optional): The path to write temp files.
    """

    def __init__(self, temp_path=None):
        """Initialize the Class properties."""
        self.temp_path = temp_path or '/tmp'

        # properties
        self._camel_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        self._inflect = None
        self.variable_match = re.compile(fr'^{self.variable_pattern}$')
        self.variable_parse = re.compile(self.variable_pattern)

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

    @staticmethod
    def decrypt_aes_cbc(key, ciphertext, iv=None):
        """Return AES CBC decrypted string.

        Args:
            key (bytes): The encryption key.
            ciphertext (bytes): The ciphertext to decrypt.
            iv (bytes, optional): The CBC initial vector.

        Returns:
            bytes: The encoded string.
        """
        iv = iv or b'\0' * 16

        # ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        # ensure iv is bytes
        if isinstance(iv, str):
            iv = iv.encode()

        aes_cbc_decrypt = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
        decrypted = aes_cbc_decrypt.feed(ciphertext)
        decrypted += aes_cbc_decrypt.feed()
        return decrypted

    @staticmethod
    def encrypt_aes_cbc(key, plaintext, iv=None):
        """Return AES CBC encrypted string.

        Args:
            key (bytes): The encryption key.
            plaintext (str|bytes): The text to encrypt.
            iv (bytes, optional): The CBC initial vector.

        Returns:
            bytes: The encoded string.
        """
        iv = iv or b'\0' * 16

        # ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        # ensure plaintext is bytes
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()

        # ensure iv is bytes
        if isinstance(iv, str):
            iv = iv.encode()

        aes_cbc_encrypt = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
        encrypted = aes_cbc_encrypt.feed(plaintext)
        encrypted += aes_cbc_encrypt.feed()
        return encrypted

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

    @property
    def inflect(self):
        """Return instance of inflect."""
        if self._inflect is None:
            import inflect

            self._inflect = inflect.engine()
        return self._inflect

    @staticmethod
    def is_cidr(possible_cidr_range: str) -> bool:
        """Return whether the possible_cidr_range is a CIDR range."""
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
        """Return whether the possible_ip is an IP address range."""
        try:
            ipaddress.ip_address(possible_ip)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def printable_cred(cred, visible=1, mask_char=None):
        """Return a printable (masked) version of the provided credential.

        Args:
            cred (str): The cred to print.
            visible (str): The number of characters at the beginning and
                ending of the cred to not mask.
            mask_char (str, Default: "*"): The character to use in the mask.

        Returns:
            str: The reformatted token.
        """
        mask_char = mask_char or '*'
        if cred is not None and len(cred) >= visible * 2:
            cred = f'{cred[:visible]}{mask_char * 4}{cred[-visible:]}'
        return cred

    @staticmethod
    def random_string(string_length=10):
        """Generate a random string of fixed length

        Args:
            string_length (int, optional): The length of the string. Defaults to 10.

        Returns:
            str: A random string
        """
        return ''.join(random.choice(string.ascii_letters) for i in range(string_length))

    def requests_to_curl(self, request, mask_headers=True, mask_patterns=None, verify=True):
        """Return converted PreparedRequest to a curl command.

        Args:
            request (requests.models.PreparedRequest): The response.request object.
            mask_headers (bool, default: True): If True then values for certain header
                key will be masked.
            mask_patterns (list, default: None): A list of patterns if found in headers the value
                will be masked.
            verify (bool, default: True): If False the curl command will include --insecure flag.

        Returns:
            str: The curl command.
        """
        # APP-79 - adding the ability to log request as curl commands
        cmd = ['curl', '-X', request.method]

        # add headers to curl command
        for k, v in sorted(list(dict(request.headers).items())):
            if mask_headers is True:
                patterns = [
                    'authorization',
                    'password',
                    'session',
                    'username',
                    'token',
                ]
                if isinstance(mask_patterns, list):
                    # add user defined mask patterns
                    patterns.extend(mask_patterns)

                for p in patterns:
                    if re.match(rf'.*{p}.*', k, re.IGNORECASE):
                        v = self.printable_cred(v)

                # using gzip in Accept-Encoding with CURL on the CLI produces
                # the warning "Binary output can mess up your terminal."
                if k.lower() == 'accept-encoding':
                    encodings = [e.strip() for e in v.split(',')]
                    for encoding in list(encodings):
                        if encoding in ['gzip']:
                            encodings.remove(encoding)
                    v = ', '.join(encodings)

            cmd.append(f"-H '{k}: {v}'")

        if request.body:
            # add body to the curl command
            body = request.body
            try:
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
                body_data = f'-d "{body}"'
            except Exception:
                temp_file = self.write_temp_binary_file(body)
                body_data = f'--data-binary @{temp_file}'
            cmd.append(body_data)

        if not verify:
            # add insecure flag to curl command
            cmd.append('--insecure')

        # add url to curl command
        cmd.append(request.url)

        return ' '.join(cmd)

    @staticmethod
    def snake_to_camel(snake_string):
        """Convert snake_case to camelCase

        Args:
            snake_string (str): The snake case input string.
        """
        components = snake_string.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def standardize_asn(asn: str) -> str:
        """Return the ASN formatted for ThreatConnect."""
        numbers = re.findall('[0-9]+', asn)
        if len(numbers) == 1:
            asn = f'ASN{numbers[0]}'
        return asn

    @staticmethod
    def to_bool(value):
        """Convert value to bool.

        Args:
            value (bool|str): The value to convert to boolean.

        Returns:
            bool: The boolean value
        """
        return str(value).lower() in ['1', 't', 'true', 'y', 'yes']

    def variable_method_name(self, variable):
        """Convert variable name to a valid method name.

        #App:9876:string.operation!String -> string_operation_string

        Args:
            variable (string): The variable name to convert.

        Returns:
            (str): Method name
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
    def variable_pattern(self):
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
        fqpn = os.path.join(self.temp_path, filename)
        os.makedirs(os.path.dirname(fqpn), exist_ok=True)
        with open(fqpn, mode) as fh:
            fh.write(content)
        return fqpn
