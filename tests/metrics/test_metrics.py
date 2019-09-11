# -*- coding: utf-8 -*-
"""Test the TcEx Metrics Module."""
import uuid


# pylint: disable=W0201
class TestMetrics:
    """Test the TcEx Metrics Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_add_metrics(tcex):
        """Test metrics."""
        date = '2008-12-12T12:12:12'
        result_date = '2008-12-12T00:00:00Z'
        metrics = tcex.metric(
            name='pytest metrics',
            description='pytest',
            data_type='Sum',
            interval='Daily',
            keyed=False,
        )
        results = metrics.add(value=42, date=date, return_value=True)
        metrics.add(value=24, date=date, return_value=False)
        assert results.get('date') == result_date

    @staticmethod
    def test_add_keyed_metrics(tcex):
        """Test key metrics."""
        date = '2008-12-12T12:12:12'
        result_date = '2008-12-12T00:00:00Z'
        metrics = tcex.metric(
            name='pytest metrics by Owner',
            description='pytest',
            data_type='Sum',
            interval='Daily',
            keyed=True,
        )
        results = metrics.add_keyed(value=42, key='MyOrg', date=date, return_value=True)
        assert results.get('date') == result_date

    @staticmethod
    def test_create_new_metrics(tcex):
        """Test key metrics."""
        name = 'pytest-{}'.format(str(uuid.uuid4()))
        metrics = tcex.metric(
            name=name, description='pytest', data_type='Sum', interval='Daily', keyed=True
        )
        assert metrics.metric_find()

    @staticmethod
    def test_create_new_metrics_fail(tcex):
        """Test key metrics."""
        name = 'x' * 500
        try:
            tcex.metric(
                name=name, description='pytest', data_type='Sum', interval='Daily', keyed=True
            )
            assert False, 'Failed to catch API error for metric name to long'
        except RuntimeError:
            assert True
