# -*- coding: utf-8 -*-
"""TcEx Testing Initialization."""
import os

import tcex

# a token in required for DataStore testing
if not os.getenv('TC_TOKEN'):
    raise RuntimeError('A Token is required to run tests.')

config_data = {
    'api_default_org': os.getenv('API_DEFAULT_ORG'),
    'tc_api_path': os.getenv('TC_API_PATH'),
    'tc_log_level': os.getenv('TC_LOG_LEVEL', 'debug'),
    'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
    'tc_token': os.getenv('TC_TOKEN'),
    'tc_token_expires': os.getenv('TC_TOKEN_EXPIRES'),
}
config_data['tc_proxy_tc'] = str(os.getenv('TC_PROXY_TC', 'false')).lower() in ['true']

if os.getenv('TC_PROXY_HOST'):
    config_data['tc_proxy_host'] = os.getenv('TC_PROXY_HOST')
if os.getenv('TC_PROXY_PORT'):
    config_data['tc_proxy_port'] = os.getenv('TC_PROXY_PORT')
if os.getenv('TC_PROXY_USERNAME'):
    config_data['tc_proxy_username'] = os.getenv('TC_PROXY_USERNAME')
if os.getenv('TC_PROXY_PASSWORD'):
    config_data['tc_proxy_password'] = os.getenv('TC_PROXY_PASSWORD')

tcex = tcex.TcEx()
tcex.tcex_args.config(config_data)
