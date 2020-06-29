# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""


class TestSession:
    """Test the TcEx Batch Module."""

    @staticmethod
    def test_session(tcex):
        """Test message tc method.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex.session.get('/v2/owners')
        assert r.status_code == 200
