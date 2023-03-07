"""TcEx Utilities String Operations Module"""
# standard library
import random
import re
from functools import reduce
from string import ascii_letters

# third-party
import inflect

# first-party
from tcex.backports import cached_property


class StringOperations:
    """TcEx Utilities String Operations Class"""

    @staticmethod
    def camel_string(string: str) -> 'CamelString':
        """Return str with custom properties/methods."""
        return CamelString(string)

    def camel_to_snake(self, string: str) -> str:
        """Return snake_case string from a camelCase string."""
        return self._camel_pattern.sub('_', string).lower()

    def camel_to_space(self, string: str) -> str:
        """Return space case string from a camelCase string."""
        return self._camel_pattern.sub(' ', string).lower()

    @cached_property
    def inflect(self) -> inflect.engine:
        """Return instance of inflect."""
        return inflect.engine()

    @staticmethod
    def random_string(string_length: int = 10) -> str:
        """Generate a random string of fixed length."""
        return ''.join(random.choice(ascii_letters) for _ in range(string_length))  # nosec

    @staticmethod
    def snake_string(string: str) -> 'SnakeString':
        """Return custom str with custom properties/methods."""
        return SnakeString(string)

    @staticmethod
    def snake_to_pascal(string: str) -> str:
        """Convert snake_case to PascalCase."""
        return string.replace('_', ' ').title().replace(' ', '')

    @staticmethod
    def snake_to_camel(string: str) -> str:
        """Convert snake_case to camelCase."""
        components = string.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def to_bool(value: bool | int | str) -> bool:
        """Convert value to bool."""
        return str(value).lower() in ['1', 't', 'true', 'y', 'yes']

    @staticmethod
    def truncate_string(
        string: str,
        length: int,
        append_chars: str | None = '',
        spaces: bool = False,
    ) -> str:
        """Truncate a string to a given length.

        Args:
            string: The input string to truncate.
            length: The length of the truncated string.
            append_chars: Any character that should be appended to the
                string. Typically used for ellipsis (e.g. ...).
            spaces: If True truncation will be done at the
                nearest space before the truncation length to avoid chopping words.
        """
        if string is None:
            string = ''

        if length is None:
            length = len(string)

        if len(string) <= length:
            return string

        # set sane default for append_chars
        append_chars = str(append_chars or '')

        # ensure append_chars is not longer than length
        if len(append_chars) > length:  # pragma: no cover
            raise RuntimeError('Append chars cannot exceed the truncation length.')

        output = string[0 : length - len(append_chars)]  # noqa: E203
        if spaces is True:
            if not output.endswith(' '):
                # split output on spaces and drop last item to terminate string on word
                output = ' '.join(output.split(' ')[:-1])

        return f'{output.rstrip()}{append_chars}'

    @property
    def _camel_pattern(self) -> re.Pattern:
        """Return compiled re pattern for converting to camelCase."""
        return re.compile(r'(?<!^)(?=[A-Z])')

    @staticmethod
    def wrap_string(
        line: str,
        wrap_chars: list[str] | None = None,
        length: int = 100,
        force_wrap: bool = True,
    ) -> str:
        """Wrap a long string to a given length.

        Lines will only be broken on instances of strings from wrap_chars.

        Args:
            line: the string to break into lines
            wrap_chars: list of strings line should be broken on
            length: max length for any single line
            force_wrap: if True, line will be broken even if no string from wrap_chars is available.
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
        """Return a PascalCase version of a camelCase string."""
        return CamelString(self.so.camel_to_space(self).title().replace(' ', ''))

    def plural(self):
        """Return the plural spelling of a camelCase string."""
        return CamelString(self.so.inflect.plural(self.singular()))

    def singular(self):
        """Return the singular spelling of a camelCase string."""
        try:
            _singular = self.so.inflect.singular(self)
        except Exception:
            _singular = self.so.inflect.singular_noun(self)

        if not _singular:
            _singular = self
        return CamelString(_singular)

    def snake_case(self):
        """Return a snake_case version of a camelCase string."""
        return CamelString(self.so.camel_to_snake(self))

    def space_case(self):
        """Return a "space case" version of a camelCase string."""
        return CamelString(self.so.camel_to_space(self))


class SnakeString(str):
    """Power String"""

    # properties
    so = StringOperations()

    def camel_case(self):
        """Return a camelCase version of a snake_case string."""
        return SnakeString(self.so.snake_to_camel(self))

    def pascal_case(self):
        """Return a PascalCase version of a snake_case string."""
        return SnakeString(self.so.snake_to_pascal(self))

    def plural(self):
        """Return the plural spelling of a snake_case string."""
        return SnakeString(self.so.inflect.plural(self.singular()))

    def singular(self):
        """Return the singular spelling of a snake_case string."""
        try:
            _singular = self.so.inflect.singular(self)
        except Exception:
            _singular = self.so.inflect.singular_noun(self)

        if not _singular:
            _singular = self
        return SnakeString(_singular)

    def space_case(self, title: bool = True):
        """Return a "space case" version of a snake_case string."""
        space_string = self.replace('_', ' ')
        if title is True:
            space_string = space_string.title()
        return space_string
