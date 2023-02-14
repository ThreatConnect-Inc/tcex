"""Tests for TcEx Playbook Create Module."""
# standard library
from typing import Any

# third-party
import pytest

# first-party
from tcex import TcEx  # TYPE-CHECKING
from tcex.backports import cached_property
from tcex.input.field_types import KeyValue
from tcex.playbook.playbook import Playbook  # TYPE-CHECKING
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestPlaybookCreate:
    """Tests for TcEx Playbook Create Module."""

    tc_playbook_out_variables = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.tc_playbook_out_variables = [
            '#App:0001:b1!Binary',
            '#App:0001:ba1!BinaryArray',
            '#App:0001:kv1!KeyValue',
            '#App:0001:kva1!KeyValueArray',
            '#App:0001:s1!String',
            '#App:0001:sa1!StringArray',
            '#App:0001:te1!TCEntity',
            '#App:0001:tea1!TCEntityArray',
            # '#App:0001:tee1!TCEnhanceEntity',
            '#App:0001:r1!Raw',
        ]

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @pytest.mark.parametrize(
        'key,value,expected',
        [
            ('ba1', b'bytes 1', False),
            ('#App:0002:b1!Binary', b'bytes 1', False),
            (None, b'bytes 2', True),
            ('#App:0002:b3!Binary', None, True),
        ],
    )
    def test_playbook_create_check_null(
        self, key: str, value: bytes, expected: bool, playbook: 'Playbook'
    ):
        """Test playbook variables."""
        assert playbook.create._check_null(key, value) is expected

    @pytest.mark.parametrize(
        'variable,when_requested,expected',
        [
            ('#App:0001:b1!Binary', True, True),
            ('#App:0001:kv1!KeyValue', True, True),
            ('#App:0001:s1!String', True, True),
            ('#App:0001:te1!TCEntity', True, True),
            # force create (when_requested=False)
            ('#App:0001:app.force.create!TCEntity', False, True),
            # fail tests
            ('not_a_variable', True, False),
            ('#App:0001:not.requested!TCEntity', True, False),
        ],
    )
    def test_playbook_create_check_requested(
        self, variable: str, expected: bool, when_requested: bool, playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        assert playbook.create._check_requested(variable, when_requested) is expected

    @pytest.mark.parametrize(
        'variable,type_,should_fail',
        [
            ('#App:0001:b1!Binary', 'Binary', False),
            ('#App:0001:kv1!KeyValue', 'KeyValue', False),
            ('#App:0001:s1!String', 'String', False),
            ('#App:0001:te1!TCEntity', 'TCEntity', False),
            # fail tests
            ('#App:0001:b1!Binary', 'String', True),
        ],
    )
    def test_playbook_create_check_variable_type(
        self, variable: str, type_: bool, should_fail: bool, playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        if should_fail is False:
            assert True
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create._check_variable_type(variable, type_)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'value,expected',
        [
            (True, 'true'),
            (1.1, '1.1'),
            (1, '1'),
            ('string', 'string'),
            (None, None),
        ],
    )
    def test_playbook_create_coerce_string_value(
        self, value: bool | float | int | str, expected: str, playbook: 'Playbook'
    ):
        """Test playbook variables."""
        assert playbook.create._coerce_string_value(value) == expected

    @pytest.mark.parametrize(
        'variable,variable_type,expected',
        [
            ('#App:0001:b1!Binary', None, '#App:0001:b1!Binary'),
            ('kv1', None, '#App:0001:kv1!KeyValue'),
            ('kv1', 'KeyValue', '#App:0001:kv1!KeyValue'),
            ('unknown', None, None),
            ('unknown', 'KeyValue', None),
        ],
    )
    def test_playbook_create_get_variable(
        self, variable: str, variable_type: str | None, expected: str, playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        assert playbook.create._get_variable(variable, variable_type) == expected

    # TODO: [lowest] add test for _serialize_data
    # def test_playbook_create_serialize_data()

    @pytest.mark.parametrize(
        'value,validate,allow_none,expected,should_fail',
        [
            (
                {'key': 'key', 'value': 'value'},
                True,
                False,
                {'key': 'key', 'value': 'value'},
                False,
            ),
            (
                KeyValue(**{'key': 'key', 'value': 'value'}),
                True,
                False,
                {'key': 'key', 'value': 'value'},
                False,
            ),
            # fail tests
            (None, True, False, None, True),
        ],
    )
    def test_playbook_create_process_object_types(
        self,
        value: KeyValue | dict,
        validate: bool,
        allow_none: bool,
        expected: str,
        should_fail: str,
        playbook: 'Playbook',
    ):
        """Test playbook variables."""
        if should_fail is False:
            assert playbook.create._process_object_types(value, validate, allow_none) == expected
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create._process_object_types(value, validate, allow_none)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'data,expected',
        [
            (
                {'key': 'key', 'value': 'value'},
                True,
            ),
            # fail tests
            (
                {'key1': 'key', 'value2': 'value'},
                False,
            ),
            (
                'string',
                False,
            ),
        ],
    )
    def test_playbook_create_is_key_value(
        self,
        data: dict,
        expected: bool,
        playbook: 'Playbook',
    ):
        """Test playbook variables."""
        assert playbook.create.is_key_value(data) == expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            ('#App:0001:b1!Binary', True),
            ('#App:0001:kv1!KeyValue', True),
            # fail tests
            ('kv1', False),
            (None, False),
        ],
    )
    def test_playbook_create_is_requested(
        self, variable: str, expected: bool, playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        assert playbook.create.is_requested(variable) is expected

    @pytest.mark.parametrize(
        'data,expected',
        [
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
            ),
            # fail tests
            (
                {'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            (
                'string',
                False,
            ),
        ],
    )
    def test_playbook_create_is_tc_entity(
        self,
        data: dict,
        expected: bool,
        playbook: 'Playbook',
    ):
        """Test playbook variables."""
        assert playbook.create.is_tc_entity(data) == expected

    @pytest.mark.parametrize(
        'key,value,validate,variable_type,when_requested,expected',
        [
            # _check_null
            (None, b'123', True, None, True, None),
            # _get_variable
            ('b1', b'123', True, None, True, b'123'),
            # _get_variable w/type
            ('b1', b'123', True, 'Binary', True, b'123'),
            # when requested_check=True (return None)
            ('#App:0001:not-requested!Binary', b'123', True, None, True, None),
            # when requested_check=False (force write)
            ('#App:0001:not-requested!Binary', b'123', True, None, False, b'123'),
            # using full variable as key
            ('#App:0001:b1!Binary', b'123', True, None, True, b'123'),
        ],
    )
    def test_playbook_create_any(
        self,
        key: str,
        value: Any,
        validate: bool,
        variable_type: str,
        when_requested: bool,
        expected: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        playbook.create.any(key, value, validate, variable_type, when_requested)
        assert playbook.read.variable(playbook.create._get_variable(key, variable_type)) == expected

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, b'123', True, True, None, False),
            # _get_variable
            ('b1', b'123', True, True, b'123', False),
            # when requested_check=True (return None)
            ('#App:0001:not-requested!Binary', b'123', True, True, None, False),
            # when requested_check=False (force write)
            ('#App:0001:not-requested!Binary', b'123', True, False, b'123', False),
            # using full variable as key
            ('#App:0001:b1!Binary', b'123', True, True, b'123', False),
            # fail tests
            ('#App:0001:b1!Binary', 'not binary 1', True, True, None, True),
            ('#App:0001:b1!Binary', [], True, True, None, True),
            ('#App:0001:b1!Binary', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_binary_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'Binary')

        if should_fail is False:
            playbook.create.binary(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.binary(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, [b'123'], True, True, None, False),
            # _get_variable
            ('ba1', [b'123'], True, True, [b'123'], False),
            # when requested_check=True (return None)
            ('#App:0001:not-requested!BinaryArray', [b'123'], True, True, None, False),
            # when requested_check=False (force write)
            ('#App:0001:not-requested!BinaryArray', [b'123'], True, False, [b'123'], False),
            # using full variable as key
            ('#App:0001:ba1!BinaryArray', [b'123'], True, True, [b'123'], False),
            # fail tests
            ('#App:0001:ba1!BinaryArray', 'not binary 1', True, True, None, True),
            ('#App:0001:ba1!BinaryArray', [b'123', 'abc'], True, True, None, True),
            ('#App:0001:ba1!BinaryArray', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_binary_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'BinaryArray')

        if should_fail is False:
            playbook.create.binary_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.binary_array(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, {'key': 'key', 'value': 'value'}, True, True, None, False),
            # _get_variable
            (
                'kv1',
                {'key': 'key', 'value': 'value'},
                True,
                True,
                {'key': 'key', 'value': 'value'},
                False,
            ),
            # when requested_check=True (return None)
            (
                '#App:0001:not-requested!KeyValue',
                {'key': 'key', 'value': 'value'},
                True,
                True,
                None,
                False,
            ),
            # when requested_check=False (force write)
            (
                '#App:0001:not-requested!KeyValue',
                {'key': 'key', 'value': 'value'},
                True,
                False,
                {'key': 'key', 'value': 'value'},
                False,
            ),
            # using full variable as key
            (
                '#App:0001:kv1!KeyValue',
                {'key': 'key', 'value': 'value'},
                True,
                True,
                {'key': 'key', 'value': 'value'},
                False,
            ),
            # fail tests
            ('#App:0001:kv1!KeyValue', 'not key value 1', True, True, None, True),
            ('#App:0001:kv1!KeyValue', [], True, True, None, True),
            ('#App:0001:kv1!KeyValue', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_key_value_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'KeyValue')

        if should_fail is False:
            playbook.create.key_value(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.key_value(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, [{'key': 'key', 'value': 'value'}], True, True, None, False),
            # _get_variable
            (
                'kva1',
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                [{'key': 'key', 'value': 'value'}],
                False,
            ),
            # when requested_check=True (return None)
            (
                '#App:0001:not-requested!KeyValueArray',
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                None,
                False,
            ),
            # when requested_check=False (force write)
            (
                '#App:0001:not-requested!KeyValueArray',
                [{'key': 'key', 'value': 'value'}],
                True,
                False,
                [{'key': 'key', 'value': 'value'}],
                False,
            ),
            # using full variable as key
            (
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                [{'key': 'key', 'value': 'value'}],
                False,
            ),
            # fail tests
            ('#App:0001:kva1!KeyValueArray', 'not key value array 1', True, True, None, True),
            ('#App:0001:kva1!KeyValueArray', [], True, True, None, True),
            ('#App:0001:kva1!KeyValueArray', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_key_value_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'KeyValueArray')

        if should_fail is False:
            playbook.create.key_value_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.key_value(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, 'string', True, True, None, False),
            # _get_variable
            ('s1', 'string', True, True, 'string', False),
            # when requested_check=True (return None)
            ('#App:0001:not-requested!String', 'string', True, True, None, False),
            # when requested_check=False (force write)
            ('#App:0001:not-requested!String', 'string', True, False, 'string', False),
            # using full variable as key
            ('#App:0001:s1!String', 'string', True, True, 'string', False),
            # fail tests
            ('#App:0001:s1!String', b'not String 1', True, True, None, True),
            ('#App:0001:s1!String', [], True, True, None, True),
            ('#App:0001:s1!String', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:b1!Binary', b'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_string_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'String')

        if should_fail is False:
            playbook.create.string(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.string(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, ['string'], True, True, None, False),
            # _get_variable
            ('sa1', ['string'], True, True, ['string'], False),
            # when requested_check=True (return None)
            ('#App:0001:not-requested!StringArray', ['string'], True, True, None, False),
            # when requested_check=False (force write)
            ('#App:0001:not-requested!StringArray', ['string'], True, False, ['string'], False),
            # using full variable as key
            ('#App:0001:sa1!StringArray', ['string'], True, True, ['string'], False),
            # fail tests
            ('#App:0001:sa1!StringArray', 'not string array 1', True, True, None, True),
            ('#App:0001:sa1!StringArray', ['string', b'abc'], True, True, None, True),
            ('#App:0001:sa1!StringArray', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:b1!Binary', b'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_string_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'StringArray')

        if should_fail is False:
            playbook.create.string_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.string_array(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, {'id': 123, 'type': 'Address', 'value': '1.1.1.1'}, True, True, None, False),
            # _get_variable
            (
                'te1',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                True,
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            # when requested_check=True (return None)
            (
                '#App:0001:not-requested!TCEntity',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                True,
                None,
                False,
            ),
            # when requested_check=False (force write)
            (
                '#App:0001:not-requested!TCEntity',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                False,
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            # using full variable as key
            (
                '#App:0001:te1!TCEntity',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                True,
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            # fail tests
            ('#App:0001:te1!TCEntity', 'not key value 1', True, True, None, True),
            ('#App:0001:te1!TCEntity', [], True, True, None, True),
            ('#App:0001:te1!TCEntity', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_tc_entity_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'TCEntity')

        if should_fail is False:
            playbook.create.tc_entity(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.tc_entity(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}], True, True, None, False),
            # _get_variable
            (
                'tea1',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                False,
            ),
            # when requested_check=True (return None)
            (
                '#App:0001:not-requested!TCEntityArray',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                None,
                False,
            ),
            # when requested_check=False (force write)
            (
                '#App:0001:not-requested!TCEntityArray',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                False,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                False,
            ),
            # using full variable as key
            (
                '#App:0001:tea1!TCEntityArray',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                False,
            ),
            # fail tests
            ('#App:0001:tea1!TCEntityArray', 'not tc entity array 1', True, True, None, True),
            ('#App:0001:tea1!TCEntityArray', ['not tc entity'], True, True, None, True),
            ('#App:0001:tea1!TCEntityArray', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_tc_entity_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: 'MockApp',
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'TCEntityArray')

        if should_fail is False:
            playbook.create.tc_entity_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.tc_entity_array(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)
