# -*- coding: utf-8 -*-
"""TcEx Playbook Common module"""
import json
import os

from .test_case import TestCase


class TestCasePlaybookCommon(TestCase):
    """Playbook TestCase Class"""

    _output_variables = None
    context_tracker = []
    redis_client = None
    redis_staging_data = {
        '#App:1234:empty!String': '',
        '#App:1234:null!String': None,
        '#App:1234:non-ascii!String': 'ドメイン.テスト',
    }

    @property
    def default_args(self):
        """Return App default args."""
        args = super().default_args
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

    @property
    def output_variables(self):
        """Return playbook output variables"""
        if self._output_variables is None:
            output_variables = self.install_json.get('playbook', {}).get('outputVariables') or []
            self._output_variables = self.output_variable_creator(output_variables)
        return self._output_variables

    @staticmethod
    def output_variable_creator(output_variables, job_id=9876):
        """Create output variables.

        Args:
            output_variables (dict): A dict of the output variables
            job_id (int): A job id to use in output variable string.
        """
        variables = []
        if output_variables is None:
            output_variables = []

        for p in output_variables:
            # "#App:9876:app.data.count!String"
            variables.append(f"#App:{job_id}:{p.get('name')}!{p.get('type')}")
        return variables

    def populate_output_variables(self):
        """Generate validation rules from App outputs."""
        profile_filename = os.path.join(self.test_case_profile_dir, f'{self.profile_name}.json')
        with open(profile_filename, 'r+') as fh:
            profile_data = json.load(fh)
            # get current permutations to ensure only valid output variables are included.
            pov = profile_data.get('permutation_output_variables')
            if pov is not None:
                pov = self.output_variable_creator(pov)

            outputs = {}
            # for context in self.context_tracker:
            while self.context_tracker:
                context = self.context_tracker.pop(0)
                # get all current keys in current context
                redis_data = self.redis_client.hgetall(context)
                trigger_id = self.redis_client.hget(context, '_trigger_id')

                for variable in self.output_variables:
                    if pov is not None and variable not in pov:
                        # variable is not in permutation output variables
                        continue

                    # get data from redis for current context
                    data = redis_data.get(variable.encode('utf-8'))

                    # validate redis variables
                    if data is None:
                        # log error for missing output data
                        self.log.error(
                            f'[{self.profile_name}] Missing redis output for variable {variable}'
                        )
                    else:
                        data = json.loads(data.decode('utf-8'))

                    # validate validation variables
                    validation_output = (profile_data.get('outputs') or {}).get(variable)
                    if (
                        trigger_id is None
                        and validation_output is None
                        and profile_data.get('outputs') is not None
                    ):
                        self.log.error(
                            f'[{self.profile_name}] Missing validations rule: {variable}'
                        )
                    output_data = {'expected_output': data, 'op': 'eq'}

                    # make business rules based on data type or content
                    if variable.endswith('json.raw!String'):
                        output_data = {'expected_output': data, 'op': 'jeq'}

                    # get trigger id for service Apps
                    if trigger_id is not None:
                        if isinstance(trigger_id, bytes):
                            trigger_id = trigger_id.decode('utf-8')
                        outputs.setdefault(trigger_id, {})
                        outputs[trigger_id][variable] = output_data
                    else:
                        outputs[variable] = output_data

            if profile_data.get('outputs') is None:
                # update the profile
                profile_data['outputs'] = outputs

                fh.seek(0)
                fh.write(json.dumps(profile_data, indent=2, sort_keys=True))
                fh.truncate()

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)

    def teardown_method(self):
        """Run after each test method runs."""
        if self.enable_update_profile:
            self.populate_output_variables()
        self.context_tracker = []
        # delete redis context data after populate_output_variable
        r = self.stager.redis.delete_context(self.context)
        self.log_data('teardown method', 'delete count', r)
        # delete threatconnect staged data
        self.stager.threatconnect.delete_staged(self._staged_tc_data)
        super().teardown_method()
