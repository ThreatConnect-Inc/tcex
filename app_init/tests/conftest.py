# -*- coding: utf-8 -*-
"""Test HTTP Client Advanced Basic Auth Module."""
import pytest

from tcex import TcEx

# from tcex.testing import RunApp, StageData, ValidateData, default_args
from tcex.testing import Stager, default_args


@pytest.fixture(scope='session', params=None, autouse=False)
def _tcex():
    """Return an instance of TcEx"""
    t = TcEx()
    t.args.config(default_args)
    return t


# @pytest.fixture(scope='session', params=None, autouse=False)
# def runner():
#     """Return an instance of StageData"""
#     return RunApp()

# possible scopes - session, module, class and  function
@pytest.fixture(scope='session', params=None, autouse=False)
def stager(_tcex):
    """Return an instance of StageData"""
    return Stager(_tcex)


# @pytest.fixture(scope='session', params=None, autouse=False)
# def validator(_tcex):
#     """Return an instance of StageData"""
#     return ValidateData(_tcex)
