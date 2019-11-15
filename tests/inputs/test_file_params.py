# -*- coding: utf-8 -*-
"""Test the TcEx Inputs Config Module."""
import os
import sys

from tcex import TcEx


# pylint: disable=W0201
class TestInputsFileParams:
    """Test TcEx File Params Inputs."""

    @staticmethod
    def test_file_params():
        """Test encrypted file params input."""

        os.environ['TC_APP_PARAM_FILE'] = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'app_params.aes'
        )
        os.environ['TC_APP_PARAM_KEY'] = 'NdwGwTuWjEXyuLLE'

        # clear sys.argv to avoid invalid arguments
        sys_argv_orig = sys.argv
        sys.argv = sys.argv[:1]

        # initialize tcex and add required argument
        fp_tcex = TcEx()

        # assert args
        assert fp_tcex.args.tc_api_path == 'https://localhost:8443/api'
        assert fp_tcex.args.tc_svc_server_topic == 'svc-server-c1fb3cd06ff44e814fa87e4b928fe13d'
        assert fp_tcex.args.service_id == 'c1fb3cd06ff44e814fa87e4b928fe13d'

        # reset sys.argv
        sys.argv = sys_argv_orig

        try:
            del os.environ['TC_APP_PARAM_FILE']
            del os.environ['TC_APP_PARAM_KEY']
        except Exception:
            pass
