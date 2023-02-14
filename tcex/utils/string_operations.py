"""TcEx Utilities String Operations Module"""
# standard library
import random
import re
import string
from functools import reduce

# first-party
from tcex.backports import cached_property


class StringOperations:
    """TcEx Utilities String Operations Class"""

    @staticmethod
    def camel_string(string_: str) -> 'CamelString':
        """Return custom str with custom properties/methods."""
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

    @cached_property
    def inflect(self) -> 'inflect.engine':
        """Return instance of inflect."""
        # third-party
        import inflect

        return inflect.engine()

    @staticmethod
    def random_string(string_length: int = 10) -> str:
        """Generate a random string of fixed length

        Args:
            string_length: The length of the string.
        """
        return ''.join(random.choice(string.ascii_letters) for _ in range(string_length))  # nosec

    @staticmethod
    def snake_string(string_: str) -> 'SnakeString':
        """Return custom str with custom properties/methods."""
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
    def to_bool(value: bool | int | str) -> bool:
        """Convert value to bool.

        Args:
            value: The value to convert to boolean.
        """
        return str(value).lower() in ['1', 't', 'true', 'y', 'yes']

    @staticmethod
    def truncate_string(
        t_string: str,
        length: int,
        append_chars: str | None = '',
        spaces: bool = False,
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

    @property
    def _camel_pattern(self) -> 're.Pattern':
        """Return compiled re pattern."""
        return re.compile(r'(?<!^)(?=[A-Z])')

    @staticmethod
    def wrap_string(
        line: str,
        wrap_chars: list[str] | None = None,
        length: int = 100,
        force_wrap=True,
    ) -> str:
        """Wrap a long string to a given length.

        Lines will only be broken on instances of strings from wrap_chars.

        Params:
            line - the string to break into lines
            wrap_chars - list of strings line should be broken on
            length - max length for any single line
            force_wrap - if True, line will be broken even if no string from wrap_chars is
                available
        """
        wrap_chars = wrap_chars or [' ']

        # if line is already shorter than max length, we're all good!
        if len(line) < length:
            return line

        def _tokenize(acc, curr):
            """Tokenize the input into strings and separators (from wrap_chars)."""
            if curr in wrap_chars:
                return acc + [curr] + ['']
            if len(acc[-1]) == length and force_wrap:
                return acc + [curr]
            acc[-1] += curr
            return acc

        tokens = reduce(_tokenize, line, [''])

        def _chop(acc, curr):
            """Build strings in acc such that no string is greater than length chars.

            Breaks at chars in wrap_chars.
            """
            if len(acc[-1]) + len(curr) < length:
                acc[-1] += curr
                return acc
            return acc + [curr]

        lines = reduce(_chop, tokens, [''])

        return '\n'.join(lines).strip()


class CamelString(str):
    """Power String"""

    # properties
    so = StringOperations()

    def pascal_case(self):
        """Return camel case version of string."""
        return CamelString(self.so.camel_to_space(self).title().replace(' ', ''))

    def plural(self):
        """Return inflect.plural spelling of string."""
        return CamelString(self.so.inflect.plural(self.singular()))

    def singular(self):
        """Return inflect.singular spelling of string."""
        try:
            _singular = self.so.inflect.singular(self)
        except Exception:
            _singular = self.so.inflect.singular_noun(self)

        if not _singular:
            _singular = self
        return CamelString(_singular)

    def snake_case(self):
        """Return camel case version of string."""
        return CamelString(self.so.camel_to_snake(self))

    def space_case(self):
        """Return string snake to camel."""
        return CamelString(self.so.camel_to_space(self))  # type: ignore


class SnakeString(str):
    """Power String"""

    # properties
    so = StringOperations()

    def camel_case(self):
        """Return camel case version of string."""
        return SnakeString(self.so.snake_to_camel(self))

    def pascal_case(self):
        """Return camel case version of string."""
        return SnakeString(self.so.snake_to_pascal(self))

    def plural(self):
        """Return inflect.plural spelling of string."""
        return SnakeString(self.so.inflect.plural(self.singular()))

    def singular(self):
        """Return inflect.singular spelling of string."""
        try:
            _singular = self.so.inflect.singular(self)
        except Exception:
            _singular = self.so.inflect.singular_noun(self)

        if not _singular:
            _singular = self
        return SnakeString(_singular)

    def space_case(self):
        """Return a space case version of a string

        _ will be replaced with spaces.
        """
        return self.replace('_', ' ').title()
