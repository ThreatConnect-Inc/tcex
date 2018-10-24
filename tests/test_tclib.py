#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from .test_tcinit import test_create_job_app as create_job_app
from .test_tcinit import _run_subprocess

PATH_TO_TCLIB = os.path.abspath(os.path.join(os.path.dirname(__file__), "./../bin/tclib"))


def test_tclib_without_package():
    """Run the tclib command outside of a package."""
    output = _run_subprocess([PATH_TO_TCLIB])
    print(output)
    assert 'A requirements.txt file is required to install modules.' in output['stdout']


def test_tclib_without_args():
    """Run the tclib command without arguments."""
    # create a job app
    create_job_app()
    output = _run_subprocess([PATH_TO_TCLIB], reset_testing_dir=False)
    print(output)
    assert 'Traceback' not in output['stdout']
    # TODO: add more checks here...
    assert '' in output['stdout']
