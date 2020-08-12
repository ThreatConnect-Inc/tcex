# -*- coding: utf-8 -*-
"""TcEx Playbook Common module"""
# import json
# standard library
import os
import time
import uuid

from .test_case import TestCase


class TestCasePlaybookCommon(TestCase):
    """Playbook TestCase Class"""

    redis_client = None
    redis_staging_data = {
        '#App:1234:empty!Binary': '',
        '#App:1234:empty!BinaryArray': [],
        # tcex won't let these be staged
        # '#App:1234:empty!KeyValue': {},
        # '#App:1234:empty!KeyValueArray': [],
        '#App:1234:empty!String': '',
        '#App:1234:empty!StringArray': [],
        # tcex won't let these be staged
        # '#App:1234:empty!TCEntity': {},
        # '#App:1234:empty!TCEntityArray': [],
        '#App:1234:non-ascii!String': 'ドメイン.テスト',
        # staging the data is not required
        # '#App:1234:null!Binary': None,
        # '#App:1234:null!BinaryArray': None,
        # '#App:1234:null!KeyValue': None,
        # '#App:1234:null!KeyValueArray': None,
        # '#App:1234:null!String': None,
        # '#App:1234:null!StringArray': None,
        # '#App:1234:null!TCEntity': None,
        # '#App:1234:null!TCEntityArray': None,
    }

    def setup_method(self):
        """Run before each test method runs."""
        super().setup_method()
        # APP-78 - The unique redis data that will be regenerated each test method.
        redis_unique_staged_data = {
            '#App:1234:epoch!String': str(int(time.time())),
            '#App:1234:uuid!String': str(uuid.uuid4()),
        }
        self.redis_staging_data.update(redis_unique_staged_data)

    def clear_context(self, context):
        """Delete data in redis"""
        keys = self.redis_client.hkeys(context)
        if keys:
            return self.redis_client.hdel(context, *keys)
        return 0

    @property
    def default_args(self):
        """Return App default args."""
        args = super().default_args.copy()
        args.update(
            {
                'tc_playbook_db_context': self.context,
                'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
                'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
                'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
                'tc_playbook_out_variables': '',
            }
        )
        return args

    def run(self):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

    def teardown_method(self):
        """Run after each test method runs."""
        if self.enable_update_profile:
            self.log.title('Update Outputs')
            self.profile.update_outputs()

        # clear context tracker
        self.profile._context_tracker = []

        # run test_case teardown_method
        super().teardown_method()
