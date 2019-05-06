# -*- coding: utf-8 -*-
"""TcEx Testing Initialization."""
import os

from tcex import TcEx

# a token in required for DataStore testing
if not os.getenv('TC_TOKEN'):
    raise RuntimeError('A Token is required to run tests.')

config_data = {
    # connection
    'api_default_org': os.getenv('API_DEFAULT_ORG'),
    'tc_token': os.getenv('TC_TOKEN'),
    'tc_token_expires': os.getenv('TC_TOKEN_EXPIRES'),
    'tc_owner': os.getenv('TC_OWNER', 'TCI'),
    # logging
    'tc_log_level': os.getenv('TC_LOG_LEVEL', 'debug'),
    'tc_log_to_api': str(os.getenv('TC_LOG_TO_API', 'false')).lower() in ['true'],
    # paths
    'tc_api_path': os.getenv('TC_API_PATH'),
    'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
    'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
    'tc_out_path': os.getenv('TC_OUT_API', 'log'),
    'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
    # playbooks
    'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
    'tc_playbook_db_context': os.getenv(
        'TC_PLAYBOOK_DB_CONTEXT', '0d5a675a-1d60-4679-bd01-3948d6a0a8bd'
    ),
    'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
    'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
    # proxy
    'tc_proxy_tc': str(os.getenv('TC_PROXY_TC', 'false')).lower() in ['true'],
    'tc_proxy_external': str(os.getenv('TC_PROXY_EXTERNAL', 'false')).lower() in ['true'],
}

# proxy
if os.getenv('TC_PROXY_HOST'):
    config_data['tc_proxy_host'] = os.getenv('TC_PROXY_HOST')
if os.getenv('TC_PROXY_PORT'):
    config_data['tc_proxy_port'] = os.getenv('TC_PROXY_PORT')
if os.getenv('TC_PROXY_USERNAME'):
    config_data['tc_proxy_username'] = os.getenv('TC_PROXY_USERNAME')
if os.getenv('TC_PROXY_PASSWORD'):
    config_data['tc_proxy_password'] = os.getenv('TC_PROXY_PASSWORD')

tcex = TcEx()
tcex.tcex_args.config(config_data)
args = tcex.args
