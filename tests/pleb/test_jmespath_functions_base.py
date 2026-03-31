"""Tests for tcex.pleb._jmespath_functions_base (JmespathFunctionsBase)."""

import pytest

from tcex.pleb.jmespath_custom import TcFunctions


class TestJmespathFunctionsBase:
    """Tests for _parse_go_duration and _format_duration."""

    def setup_method(self) -> None:
        self.base = TcFunctions()
