"""Tests for tcex.pleb.jmespath_custom (jmespath_options, TcFunctions)."""

import collections

import jmespath
import pytest
from jmespath import exceptions

from tcex.pleb.jmespath_custom import TcFunctions, jmespath_options


# ---------------------------------------------------------------------------
# jmespath_options
# ---------------------------------------------------------------------------
class TestJmespathOptions:
    """Verify that jmespath_options() returns correctly configured Options."""

    def test_returns_options_instance(self) -> None:
        opts = jmespath_options()
        assert isinstance(opts, jmespath.Options)

    def test_custom_functions_is_tc_functions(self) -> None:
        opts = jmespath_options()
        assert isinstance(opts.custom_functions, TcFunctions)

    def test_dict_cls_is_ordered_dict(self) -> None:
        opts = jmespath_options()
        assert opts.dict_cls is collections.OrderedDict


# ---------------------------------------------------------------------------
# TcFunctions._validate_arguments and _type_check
# ---------------------------------------------------------------------------
class TestTcFunctions:
    """Tests for _validate_arguments and _type_check on TcFunctions."""

    def setup_method(self) -> None:
        self.tc = TcFunctions()

    def test_validate_arguments_empty_signature_no_error(self) -> None:
        self.tc._validate_arguments([], (), 'test')

    def test_validate_arguments_exact_count_ok(self) -> None:
        sig = ({'types': ['string']},)
        self.tc._validate_arguments(['hello'], sig, 'test')

    def test_validate_arguments_too_few_raises_arity_error(self) -> None:
        sig = ({'types': ['string']}, {'types': ['number']})
        with pytest.raises(exceptions.ArityError):
            self.tc._validate_arguments([], sig, 'test')

    def test_validate_arguments_too_many_raises_arity_error(self) -> None:
        sig = ({'types': ['string']},)
        with pytest.raises(exceptions.ArityError):
            self.tc._validate_arguments(['a', 'b', 'c'], sig, 'test')

    def test_validate_arguments_variadic_min_count_ok(self) -> None:
        sig = ({'types': ['string']}, {'types': ['string'], 'variadic': True})
        self.tc._validate_arguments(['a', 'b', 'c'], sig, 'test')

    def test_validate_arguments_variadic_too_few_raises(self) -> None:
        sig = ({'types': ['string']}, {'types': ['string'], 'variadic': True})
        with pytest.raises(exceptions.VariadictArityError):
            self.tc._validate_arguments(['only_one'], sig, 'test')

    def test_type_check_valid_type_passes(self) -> None:
        sig = ({'types': ['string']},)
        self.tc._type_check(['hello'], sig, 'test')

    def test_type_check_wrong_type_raises(self) -> None:
        from jmespath.exceptions import JMESPathTypeError

        sig = ({'types': ['string']},)
        with pytest.raises(JMESPathTypeError):
            self.tc._type_check([42], sig, 'test')

    def test_type_check_empty_types_allows_any(self) -> None:
        sig = ({'types': []},)
        self.tc._type_check([42], sig, 'test')
        self.tc._type_check(['hello'], sig, 'test')
        self.tc._type_check([None], sig, 'test')
