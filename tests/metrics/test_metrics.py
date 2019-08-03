# -*- coding: utf-8 -*-
"""Test the TcEx Metrics Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestMetrics:
    """Test the TcEx Metrics Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_metrics():
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
        assert results.get('date') == result_date

    @staticmethod
    def test_metrics_keyed():
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
