#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from .test_tcinit import test_create_job_app as create_job_app
from .test_tcinit import _run_subprocess

PATH_TO_TCRUN = os.path.abspath(os.path.join(os.path.dirname(__file__), "./../bin/tcrun"))


def test_tcrun_without_package():
    """Run the tcrun command outside of a package."""
    output = _run_subprocess([PATH_TO_TCRUN])
    assert 'Provided config file does not exist (tcex.json)' in output['stderr']


def test_tcrun_without_args():
    """Run the tcrun command without arguments."""
    # create a job app
    create_job_app()
    output = _run_subprocess([PATH_TO_TCRUN], reset_testing_dir=False)
    print(output)
    assert 'Traceback' not in output['stdout']
    # TODO: add more checks here...
    assert '' in output['stdout']
