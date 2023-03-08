"""Test the TcEx Metrics Module."""
# standard library
import uuid

# first-party
from tcex.tcex import TcEx


class TestMetrics:
    """Test the TcEx Metrics Module."""

    @staticmethod
    def test_add_metrics(tcex: TcEx):
        """Test **add** method of TcEx metrics module.

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        date = '2008-12-12T12:12:12'
        result_date = '2008-12-12T00:00:00Z'
        metrics = tcex.api.tc.v2.metric(
            name='pytest metrics',
            description='pytest',
            data_type='Average',
            interval='Daily',
            keyed=False,
        )
        results = metrics.add(value=42, date=date, return_value=True, weight=4)
        metrics.add(value=24, date=date, return_value=False)
        assert results.get('date') == result_date

    @staticmethod
    def test_add_keyed_metrics(tcex: TcEx):
        """Test **add_keyed** method of TcEx metrics module.

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        date = '2008-12-12T12:12:12'
        result_date = '2008-12-12T00:00:00Z'
        metrics = tcex.api.tc.v2.metric(
            name='pytest metrics by Owner',
            description='pytest',
            data_type='Average',
            interval='Daily',
            keyed=True,
        )
        results = metrics.add_keyed(value=42, key='MyOrg', date=date, return_value=True, weight=4)
        assert results.get('date') == result_date

    @staticmethod
    def test_create_new_metrics(tcex: TcEx):
        """Test creation of a new metric

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        name = f'pytest-{str(uuid.uuid4())}'
        metrics = tcex.api.tc.v2.metric(
            name=name, description='pytest', data_type='Sum', interval='Daily', keyed=True
        )
        assert metrics.metric_find()

    @staticmethod
    def test_create_new_metrics_fail(tcex: TcEx):
        """Test failure of a new metric creation

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        name = 'x' * 500
        try:
            tcex.api.tc.v2.metric(
                name=name, description='pytest', data_type='Sum', interval='Daily', keyed=True
            )
            assert False, 'Failed to catch API error for metric name to long'
        except RuntimeError:
            assert True
