"""TcEx Utilities Module"""
# standard library
import ipaddress
import os
import random
import re
import string
import tempfile
import uuid
from typing import TYPE_CHECKING, Any, List, Optional, Union
from urllib.parse import urlsplit

# third-party
import arrow
import jmespath
import pyaes

# first-party
from tcex.backports import cached_property

if TYPE_CHECKING:
    # third-party
    from requests import Request


class Utils:
    """TcEx framework Utils Class

    Args:
        temp_path: The path to write temp files.
    """

    def __init__(self, temp_path: Optional[str] = None):
        """Initialize the Class properties."""
        self.temp_path = temp_path or tempfile.gettempdir() or '/tmp'  # nosec

        # properties
        self._camel_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        self.variable_match = re.compile(fr'^{self.variable_pattern}$')
        self.variable_parse = re.compile(self.variable_pattern)

    @classmethod
    def any_to_arrow(cls, datetime_expression: str) -> 'arrow.Arrow':
        """Return a arrow object from datetime expression."""
        if isinstance(datetime_expression, arrow.Arrow):
            return datetime_expression

        value = str(datetime_expression)

        # note: order matters. For example, the timestamp could parse inputs that would have
        # been meant for one of the default parser formats
        parser_methods = [
            cls._parse_default_arrow_formats,
            cls._parse_non_default_arrow_formats,
            cls._parse_timestamp,
            cls._parse_humanized_input,
        ]
        for method in parser_methods:
            try:
                return method(value)
            # TypeError should never occur, but adding for completeness in case of improperly
            # overriden str method
            except (arrow.parser.ParserError, ValueError, TypeError):
                # value could not be parsed by current method.
                pass

        raise RuntimeError(
            f'Value "{value}" of type "{type(datetime_expression)}" '
            'could not be parsed as a date time object.'
        )

    def camel_string(self, string_: str) -> Any:
        """Return custom str with custom properties/methods."""

        # methods for class
        inflect = self.inflect
        camel_to_snake = self.camel_to_snake
        camel_to_space = self.camel_to_space

        class CamelString(str):
            """Power String"""

            def pascal_case(self):
                """Return camel case version of string."""
                return CamelString(camel_to_space(self).title().replace(' ', ''))

            def plural(self):
                """Return inflect.singular_noun spelling of string."""
                return CamelString(inflect.plural(self.singular()))

            def singular(self):
                """Return inflect.singular_noun spelling of string."""
                _singular = inflect.singular_noun(self)
                if _singular is False:
                    _singular = self
                return CamelString(_singular)

            def snake_case(self):
                """Return camel case version of string."""
                return CamelString(camel_to_snake(self))

            def space_case(self):
                """Return string snake to camel."""
                return CamelString(camel_to_space(self))

        return CamelString(string_)

    def camel_to_snake(self, camel_string: str) -> str:
        """Return snake case string from a camel case string.

        Args:
            camel_string: The camel case input string.
        """
        return self._camel_pattern.sub('_', camel_string).lower()

    def camel_to_space(self, camel_string: str) -> str:
        """Return space case string from a camel case string.

        Args:
            camel_string: The camel case input string.
        """
        return self._camel_pattern.sub(' ', camel_string).lower()

    @staticmethod
    def decrypt_aes_cbc(
        key: bytes, ciphertext: Union[bytes, str], iv: Optional[bytes] = None
    ) -> bytes:
        """Return AES CBC decrypted string.

        Args:
            key: The encryption key.
            ciphertext: The ciphertext to decrypt.
            iv: The CBC initial vector.
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
            key: The encryption key.
            plaintext: The text to encrypt.
            iv: The CBC initial vector.
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
        """
        flat_list = []
        for sublist in lst:
            if isinstance(sublist, list):
                for item in Utils.flatten_list(sublist):
                    flat_list.append(item)
            else:
                flat_list.append(sublist)
        return flat_list

    @cached_property
    def inflect(self) -> 'inflect.engine':  # pylint: disable=no-self-use
        """Return instance of inflect."""
        # third-party
        import inflect

        return inflect.engine()

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
    def random_string(string_length: Optional[int] = 10) -> str:
        """Generate a random string of fixed length

        Args:
            string_length: The length of the string.
        """
        return ''.join(random.choice(string.ascii_letters) for _ in range(string_length))  # nosec

    def requests_to_curl(
        self,
        request: 'Request',
        mask_headers: Optional[bool] = True,
        mask_patterns: List[str] = None,
        **kwargs: Union[bool, dict],
    ) -> str:
        """Return converted Prepared Request to a curl command.

        Args:
            request: The response.request object.
            mask_headers: If True then values for certain header key will be masked.
            mask_patterns: A list of patterns if found in headers the value will be masked.
            body_limit: The size limit for the body value.
            mask_body: If True the body will be masked.
            proxies: A dict containing the proxy configuration.
            verify: If False the curl command will include --insecure flag.
            write_file: If True and the body is binary it will be written as a temp file.
        """
        body_limit: int = kwargs.get('body_limit', 100)
        proxies: dict = kwargs.get('proxies', {})
        verify: bool = kwargs.get('verify', True)
        write_file: bool = kwargs.get('write_file', False)

        # APP-79 - adding the ability to log request as curl commands
        cmd = ['curl', '-X', request.method]

        # add headers to curl command
        for k, v in sorted(list(dict(request.headers).items())):
            if mask_headers is True:
                patterns = [
                    'authorization',
                    'cookie',
                    'password',
                    'secret',
                    'session',
                    'token',
                    'username',
                ]
                if isinstance(mask_patterns, list):
                    # add user defined mask patterns
                    patterns.extend(mask_patterns)

                for p in patterns:
                    if re.match(rf'.*{p}.*', k, re.IGNORECASE):
                        v: str = self.printable_cred(v)

                # using gzip in Accept-Encoding with CURL on the CLI produces
                # the warning "Binary output can mess up your terminal."
                if k.lower() == 'accept-encoding':
                    encodings = [e.strip() for e in v.split(',')]
                    for encoding in list(encodings):
                        if encoding in ['gzip']:
                            encodings.remove(encoding)
                    v: str = ', '.join(encodings)

            cmd.append(f"-H '{k}: {v}'")

        if request.body:
            # add body to the curl command
            body = request.body
            try:
                if isinstance(body, bytes):
                    body = body.decode('utf-8')

                if kwargs.get('mask_body', False):
                    # mask_body
                    body = self.printable_cred(body)
                else:
                    # truncate body
                    body = self.truncate_string(
                        t_string=body, length=body_limit, append_chars='...'
                    )
                body_data = f'-d "{body}"'
            except Exception:
                # set static filename so that when running a large job App thousands of files do
                # no get created.
                body_data = '--data-binary @/tmp/body-file'
                if write_file is True:
                    temp_file: str = self.write_temp_binary_file(content=body, filename='curl-body')
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

    def snake_string(self, string_: str) -> Any:
        """Return custom str with custom properties/methods."""

        # methods for class
        inflect = self.inflect
        snake_to_camel = self.snake_to_camel
        snake_to_pascal = self.snake_to_pascal

        class SnakeString(str):
            """Power String"""

            def camel_case(self):
                """Return camel case version of string."""
                return SnakeString(snake_to_camel(self))

            def pascal_case(self):
                """Return camel case version of string."""
                return SnakeString(snake_to_pascal(self))

            def plural(self):
                """Return inflect.singular_noun spelling of string."""
                return SnakeString(inflect.plural(self.singular()))

            def singular(self):
                """Return inflect.singular_noun spelling of string."""
                _singular = inflect.singular_noun(self)
                if _singular is False:
                    _singular = self
                return SnakeString(_singular)

            def space_case(self):
                """Return a space case version of a string

                _ will be replaced with spaces.
                """
                return self.replace('_', ' ').title()

            # def title(self):
            #     """Return string snake to camel."""
            #     return SnakeString(self.replace('_', ' ').title())

        return SnakeString(string_)

    @staticmethod
    def snake_to_pascal(snake_string: str) -> str:
        """Convert snake_case to PascalCase

        Args:
            snake_string: The snake case input string.
        """
        return snake_string.replace('_', ' ').title().replace(' ', '')

    @staticmethod
    def snake_to_camel(snake_string: str) -> str:
        """Convert snake_case to camelCase

        Args:
            snake_string: The snake case input string.
        """
        components = snake_string.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

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

    @staticmethod
    def to_bool(value: Union[bool, int, str]) -> bool:
        """Convert value to bool.

        Args:
            value: The value to convert to boolean.
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
            t_string: The input string to truncate.
            length: The length of the truncated string.
            append_chars: Any character that should be appended to the
                string. Typically used for ellipsis (e.g. ...).
            spaces: If True truncation will be done at the
                nearest space before the truncation length to avoid chopping words.
        """
        if t_string is None:
            t_string = ''

        if length is None:
            length = len(t_string)

        if len(t_string) <= length:
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

    def write_temp_binary_file(self, content: bytes, filename: Optional[str] = None) -> str:
        """Write content to a temporary file.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.

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
            content: The file content.
            filename: The filename to use when writing the file.
            mode: The write mode ('w' or 'wb').

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

    @staticmethod
    def _parse_default_arrow_formats(value: Any) -> 'arrow.Arrow':
        """Attempt to parse value using default Arrow formats.

        The value is simply passed into Arrow's "get" method. The following are the default
        date formats (found in arrow.parser.DateTimeParser.parse_iso):

        "YYYY-MM-DD",
        "YYYY-M-DD",
        "YYYY-M-D",
        "YYYY/MM/DD",
        "YYYY/M/DD",
        "YYYY/M/D",
        "YYYY.MM.DD",
        "YYYY.M.DD",
        "YYYY.M.D",
        "YYYYMMDD",
        # Year-Day-of-year: 2020-364 == 2020-12-29T00:00:00+00:00
        "YYYY-DDDD",
        # same as above, but without separating dash
        "YYYYDDDD",
        "YYYY-MM",
        "YYYY/MM",
        "YYYY.MM",
        "YYYY",
        # ISO week date: 2011-W05-4, 2019-W17
        "W"
        """
        return arrow.get(value)

    @staticmethod
    def _parse_humanized_input(value: Any) -> 'arrow.Arrow':
        """Attempt to dehumanize time inputs. Example: 'Two hours ago'."""
        now = arrow.utcnow()
        plurals = {
            'second': 'seconds',
            'minute': 'minutes',
            'hour': 'hours',
            'day': 'days',
            'week': 'weeks',
            'month': 'months',
            'year': 'years',
        }

        if value.strip().lower() == 'now':
            return now

        # pluralize singular time terms as applicable. Arrow does not support singular terms
        terms = [plurals.get(term.lower(), term) for term in value.split()]
        value = ' '.join(terms)

        return now.dehumanize(value)

    @staticmethod
    def _parse_non_default_arrow_formats(value: Any) -> 'arrow.Arrow':
        """Attempt to parse value using non-default Arrow formats

        These are formats that Arrow provides constants for but are not used in the "get"
        method (Arrow method that parses values into datetimes) by default.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        return arrow.get(
            value,
            [
                arrow.FORMAT_ATOM,
                arrow.FORMAT_COOKIE,
                arrow.FORMAT_RFC822,
                arrow.FORMAT_RFC850,
                arrow.FORMAT_RFC1036,
                arrow.FORMAT_RFC1123,
                arrow.FORMAT_RFC2822,
                arrow.FORMAT_RFC3339,
                arrow.FORMAT_RSS,
                arrow.FORMAT_W3C,
            ],
        )

    @staticmethod
    def _parse_timestamp(value: Any) -> 'arrow.Arrow':
        """Attempt to parse epoch timestamp in seconds, milliseconds, or microseconds.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        # note: order matters. Must try to parse as milliseconds/microseconds first (x)
        # before trying to parse as seconds (X), else error occurs if passing a ms/ns value
        try:
            # attempt to parse as string first using microsecond/millisecond and second specifiers
            return arrow.get(value, ['x', 'X'])
        except (arrow.parser.ParserError, ValueError):
            # could not parse as string, try to parse as float
            return arrow.get(float(value))
