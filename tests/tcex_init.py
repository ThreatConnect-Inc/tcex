# -*- coding: utf-8 -*-
"""TcEx Testing Initialization."""
import os

import tcex

config_data = {
    'api_default_org': os.environ.get('API_DEFAULT_ORG'),
    'tc_api_path': os.environ.get('TC_API_PATH'),
    'tc_log_level': 'debug',
    'tc_log_path': 'log',
    'tc_proxy_tc': False,
}
if os.environ.get('TC_TOKEN'):
    config_data['tc_token'] = os.environ.get('TC_TOKEN')
    config_data['tc_token_expires'] = os.environ.get('TC_TOKEN_EXPIRES')
else:
    config_data['api_access_id'] = os.environ.get('API_ACCESS_ID')
    config_data['api_secret_key'] = os.environ.get('API_SECRET_KEY')

if os.environ.get('TC_PROXY_HOST'):
    config_data['tc_proxy_host'] = os.environ.get('TC_PROXY_HOST')
if os.environ.get('TC_PROXY_PORT'):
    config_data['tc_proxy_port'] = os.environ.get('TC_PROXY_PORT')
if os.environ.get('TC_PROXY_USERNAME'):
    config_data['tc_proxy_username'] = os.environ.get('TC_PROXY_USERNAME')
if os.environ.get('TC_PROXY_PASSWORD'):
    config_data['tc_proxy_password'] = os.environ.get('TC_PROXY_PASSWORD')

tcex = tcex.TcEx()
tcex.tcex_args.config(config_data)
