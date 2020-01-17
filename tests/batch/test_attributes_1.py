# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest


class TestAttributes:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'name,description,attr_type,attr_value,displayed,source',
        [
            (
                'pytest-adversary-i1-001',
                'Attribute Testing',
                'Description',
                'Pytest',
                True,
                'pytest-testing',
            )
        ],
    )
    def test_attributes(  # pylint: disable=unused-argument
        self, name, description, attr_type, attr_value, displayed, source, tcex
    ):
        """Test batch attributes creation"""
        batch = tcex.batch(owner='TCI')
        xid = batch.generate_xid(['pytest', 'adversary', name])
        ti = batch.adversary(name=name, xid=xid)

        # security label testing - option 1
        ti.attribute(
            attr_type=attr_type,
            attr_value=attr_value,
            displayed=displayed,
            source=source,
            formatter=self.attribute_formatter,
        )

        # security label testing - option 2
        attr = ti.attribute(attr_type=attr_type, attr_value=None)
        attr.displayed = displayed
        attr.source = source

        tcex.log.debug(f'attribute data: {attr}')  # coverage: __str__ method
        assert attr.displayed == displayed
        assert attr.source == source
        assert attr.type == attr_type
        assert attr.value is None

        # submit batch
        batch.save(ti)
        batch_status = batch.submit_all()
        assert batch_status[0].get('status') == 'Completed'
        assert batch_status[0].get('successCount') == 1

    @staticmethod
    def attribute_formatter(attr_value):
        """Return formatted tag."""
        return attr_value.lower()
