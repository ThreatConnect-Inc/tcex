# -*- coding: utf-8 -*-
"""TcEx Utilities Module"""
# standard library
import ipaddress
import os
import random
import re
import string
import uuid
from typing import Any, List, Optional, Union
from urllib.parse import urlsplit

# third-party
import pyaes

from .date_utils import DatetimeUtils


class Utils:
    """TcEx framework Utils Class

    Args:
        temp_path (Optional[str] = None): The path to write temp files.
    """

    def __init__(self, temp_path: Optional[str] = None):
        """Initialize the Class properties."""
        self.temp_path = temp_path or '/tmp'  # nosec

        # properties
        self._camel_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        self._inflect = None
        self.variable_match = re.compile(fr'^{self.variable_pattern}$')
        self.variable_parse = re.compile(self.variable_pattern)

    def camel_to_snake(self, camel_string: str) -> str:
        """Return snake case string from a camel case string.

        Args:
            camel_string (str): The camel case input string.

        Returns:
            str: The snake case representation of input string.
        """
        return self._camel_pattern.sub('_', camel_string).lower()

    def camel_to_space(self, camel_string: str) -> str:
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
    def decrypt_aes_cbc(
        key: bytes, ciphertext: Union[bytes, str], iv: Optional[bytes] = None
    ) -> bytes:
        """Return AES CBC decrypted string.

        Args:
            key (bytes): The encryption key.
            ciphertext (Optional[bytes] = None): The ciphertext to decrypt.
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
    def encrypt_aes_cbc(
        key: bytes, plaintext: Union[bytes, str], iv: Optional[bytes] = None
    ) -> bytes:
        """Return AES CBC encrypted string.

        Args:
            key (bytes): The encryption key.
            plaintext (Union[bytes, str]): The text to encrypt.
            iv (Optional[bytes] = None): The CBC initial vector.

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
            # third-party
            import inflect

            self._inflect = inflect.engine()
        return self._inflect

    @staticmethod
    def is_cidr(possible_cidr_range: str) -> bool:
        """Return True if the provided value is a valid CIDR block.

        Args:
            possible_cidr_range (str): The cidr value to validate.

        Returns:
            bool: True if input is a valid CIDR.
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
            possible_ip (str): The IP value to validate.

        Returns:
            bool: True if input is a valid IP.
        """
        try:
            ipaddress.ip_address(possible_ip)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def printable_cred(
        cred: str, visible: Optional[int] = 1, mask_char: Optional[str] = '*'
    ) -> str:
        """Return a printable (masked) version of the provided credential.

        Args:
            cred (str): The cred to print.
            visible (Optional[int] = 1): The number of characters at the beginning and
                ending of the cred to not mask.
            mask_char (Optional[str] = '*'): The character to use in the mask.

        Returns:
            str: The reformatted token.
        """
        mask_char = mask_char or '*'
        if cred is not None and len(cred) >= visible * 2:
            cred = f'{cred[:visible]}{mask_char * 4}{cred[-visible:]}'
        return cred

    @staticmethod
    def random_string(string_length: Optional[int] = 10) -> str:
        """Generate a random string of fixed length

        Args:
            string_length (Optional[int] = 10): The length of the string.

        Returns:
            str: A random string
        """
        return ''.join(random.choice(string.ascii_letters) for _ in range(string_length))  # nosec

    def requests_to_curl(
        self,
        request: object,
        mask_headers: Optional[bool] = True,
        mask_patterns: List[str] = None,
        **kwargs: Union[bool, dict],
    ) -> str:
        """Return converted PreparedRequest to a curl command.

        Args:
            request (object): The response.request object.
            mask_headers (Optional[bool] = True): If True then values for certain header
                key will be masked.
            mask_patterns (list[str] = None): A list of patterns if found in headers the value
                will be masked.
            proxies (dict, kwargs): A dict containing the proxy configuration.
            verify (bool, kwargs): If False the curl command will include --insecure flag.

        Returns:
            str: The curl command.
        """
        proxies = kwargs.get('proxies', {})
        verify = kwargs.get('verify', True)

        # APP-79 - adding the ability to log request as curl commands
        cmd = ['curl', '-X', request.method]

        # add headers to curl command
        for k, v in sorted(list(dict(request.headers).items())):
            if mask_headers is True:
                patterns = [
                    'authorization',
                    'cookie',
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

        if proxies is not None and proxies.get('https'):
            # parse formatted string {'https': 'bob:pass@https://localhost:4242'}
            proxy_url: Optional[str] = proxies.get('https')
            proxy_data = urlsplit(proxy_url)

            # auth
            if proxy_data.username:
                cmd.extend(['--proxy-user', f'{proxy_data.username}:xxxxx'])

            # server
            proxy_server = proxy_data.hostname
            if proxy_data.port:
                proxy_server = f'{proxy_data.hostname}:{proxy_data.port}'
            cmd.extend(['--proxy', proxy_server])

        if not verify:
            # add insecure flag to curl command
            cmd.append('--insecure')

        # add url to curl command
        cmd.append(request.url)

        return ' '.join(cmd)

    @staticmethod
    def snake_to_camel(snake_string: str) -> str:
        """Convert snake_case to camelCase

        Args:
            snake_string (str): The snake case input string.

        Returns:
            str: The camel case string.
        """
        components = snake_string.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def standardize_asn(asn: str) -> str:
        """Return the ASN formatted for ThreatConnect.

        Args:
            asn (str): The asn value to standardize.

        Returns:
            str: The standardized asn value.
        """
        numbers = re.findall('[0-9]+', asn)
        if len(numbers) == 1:
            asn = f'ASN{numbers[0]}'
        return asn

    @staticmethod
    def to_bool(value: Union[bool, int, str]) -> bool:
        """Convert value to bool.

        Args:
            value (Union[bool, int, str]): The value to convert to boolean.

        Returns:
            bool: The boolean value
        """
        return str(value).lower() in ['1', 't', 'true', 'y', 'yes']

    @staticmethod
    def truncate_string(
        t_string: str,
        length: int,
        append_chars: Optional[str] = '',
        spaces: Optional[bool] = False,
    ) -> str:
        """Truncate a string to a given length.

        Args:
            t_string (str): The input string to truncate.
            length (int): The length of the truncated string.
            append_chars (Optional[str] = ''): Any character that should be appended to the
                string. Typically used for ellipsis (e.g. ...).
            spaces (Optional[bool] = False): If True truncation will be done at the
                nearest space before the truncation length to avoid chopping words.

        Returns:
            str: The truncated string.
        """
        if t_string in ['', None] or length is None or len(t_string) < length:
            return t_string

        # set sane default for append_chars
        append_chars = str(append_chars or '')

        # ensure append_chars is not longer than length
        if len(append_chars) > length:  # pragma: no cover
            raise RuntimeError('Append chars cannot exceed the truncation length.')

        output = t_string[0 : length - len(append_chars)]  # noqa: E203
        if spaces is True:
            if not output.endswith(' '):
                # split output on spaces and drop last item to terminate string on word
                output = ' '.join(output.split(' ')[:-1])

        return f'{output.rstrip()}{append_chars}'

    def variable_method_name(self, variable: str) -> str:
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

    def write_temp_binary_file(self, content: bytes, filename: Optional[str] = None) -> str:
        """Write content to a temporary file.

        Args:
            content (bytes): The file content.
            filename (Optional[str] = None): The filename to use when writing the file.

        Returns:
            str: Fully qualified path name for the file.
        """
        return self.write_temp_file(content, filename, 'wb')

    def write_temp_file(
        self, content: Union[bytes, str], filename: Optional[str] = None, mode: Optional[str] = 'w'
    ) -> str:
        """Write content to a temporary file.

        If passing binary data the mode needs to be set to 'wb'.

        Args:
            content (Union[bytes, str]): The file content.
            filename (Optional[str] = None): The filename to use when writing the file.
            mode (Optional[str] = 'w'): The write mode ('w' or 'wb').

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
