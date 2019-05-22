# -*- coding: utf-8 -*-
"""Testing module for TcEx Framework"""
# Copyright 2018 by ThreatConnect, Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid

from tcex.testing.stage_data import StageData  # noqa: F401
from tcex.testing.run_app import RunApp  # noqa: F401

# from tcex.testing.validate_data import RedisValidator, TcValidator
from tcex.testing.validate_data import ValidateData  # noqa: F401

# pylint: disable=W0105,W1508
# teardown - override pytest method to auto do 'stuff'

context = str(uuid.uuid4())
default_args = {
    'api_access_id': os.getenv('API_ACCESS_ID'),
    'api_default_org': os.getenv('API_DEFAULT_ORG'),
    'api_secret_key': os.getenv('API_SECRET_KEY'),
    'tc_api_path': os.getenv('TC_API_PATH'),
    'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
    'tc_log_path': os.getenv('TC_LOG_PATH', 'debug'),
    'tc_log_to_api': os.getenv('TC_LOG_TO_API', False),  # pylint: disable=invalid-envvar-default
    'tc_out_path': os.getenv('TC_OUT_PATH', 'log'),
    'tc_playbook_db_context': os.getenv('TC_PLAYBOOK_DB_CONTEXT', context),
    'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
    'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
    'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
    'tc_playbook_out_variables': '',
    'tc_proxy_external': os.getenv(
        'TC_PROXY_EXTERNAL', False
    ),  # pylint: disable=invalid-envvar-default
    'tc_proxy_host': os.getenv('TC_PROXY_HOST', 'localhost'),
    'tc_proxy_password': os.getenv('TC_PROXY_PASSWORD', None),
    'tc_proxy_port': os.getenv('TC_PROXY_PORT', '4242'),
    'tc_proxy_tc': os.getenv('TC_PROXY_TC', False),  # pylint: disable=invalid-envvar-default
    'tc_proxy_username': os.getenv(
        'TC_PROXY_USERNAME', False
    ),  # pylint: disable=invalid-envvar-default
    'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
}

""" Example Test File

from tcex.testing import RunApp, StageData, ValidateData, default_args
from dotenv import load_dotenv

# load environment variables
load_dotenv('path', '.env', verbose=True)
load_dotenv('os.getcwd()', '.env', verbose=True)

# Interface 1 - Update default Args
default_args['tc_proxy_host'] = '127.0.0.1'

# Interface 2
default_args.update({
    'count': 1,
    'tc_proxy_host': '127.0.0.1',  # example 2 override defaults
})

# Interface 3
my_args = {
    **default_args,
    'tc_playbook_db_context': '123'
}

# get instance of tcex
tcex = TcEx()
tcex.args.config(default_args)

# Stage Redis
stage_data = StageData(tcex)
stage_data.stage_redis('#App:1834:example_string!String', 'a simple string value')

# Staging Data
staging_data = [
    {
        'variable': '#App:1834:example_string!String',
        'data': 'a simple string value'
    },
    {
        'variable': '#App:1834:entities!KeyValue',
        'data': {
            'key': 'one',
            'value': '1'
        }
    },
]
stage_data.stage_redis_from_dict(staging_data)

# Stage Redis

# in pytest teardown
stage_data.clean_all()

runner = RunApp(myargs, stage_data.tcex)
runner.run('app.py', args_dict)
# do we call run.py or something else that inject args dict so we don't have to build CLI args

validator = ValidateData(tcex)
validator.validate_redis_eq('#App:1834:example_string!String', 'validation_data')

"""

"""
# test cases:
* one that uses static data that was previously downloaded
* one that downloads the data live during the run of the test

# Attack Plan
Integrations team writes the App and 60-70% of the pytest cases.

QA Hand-Off
* hand-off requirement and video of Int handoff
"""
