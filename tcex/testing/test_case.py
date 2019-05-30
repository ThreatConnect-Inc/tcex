# -*- coding: utf-8 -*-
"""TcEx testing Framework."""
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import uuid
import sys
from datetime import datetime

from tcex import TcEx
from app import App  # pylint: disable=import-error
from stage_data import Stager

logger = logging.getLogger('TestCase')
fh = RotatingFileHandler('log/tests.log', backupCount=10, maxBytes=10_485_760, mode='a')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


class TestCase(object):
    """Base TestCase Class"""

    _app_path = os.getcwd()
    _current_test = None
    _input_params = None
    _install_json = None
    _timer_class_start = None
    _timer_method_start = None
    context = None
    log = logger
    redis_staging_data = []

    @staticmethod
    def _to_bool(value):
        """Return bool value from int or string."""
        return str(value).lower() in ['1', 'true']

    def app(self, args):
        """Return an instance of App."""
        return App(self.tcex(args))

    @property
    def default_args(self):
        """Return App default args."""
        return {
            'api_access_id': os.getenv('API_ACCESS_ID'),
            'api_default_org': os.getenv('API_DEFAULT_ORG'),
            'api_secret_key': os.getenv('API_SECRET_KEY'),
            'tc_api_path': os.getenv('TC_API_PATH'),
            'tc_in_path': os.getenv('TC_IN_PATH', 'log'),
            'tc_log_level': os.getenv('TC_LOG_LEVEL', 'debug'),
            'tc_log_path': os.getenv('TC_LOG_PATH', 'log'),
            'tc_log_to_api': self._to_bool(os.getenv('TC_LOG_TO_API', 'false')),
            'tc_out_path': os.getenv('TC_OUT_PATH', 'log'),
            # 'tc_playbook_db_context': os.getenv('TC_PLAYBOOK_DB_CONTEXT', str(uuid.uuid4())),
            'tc_playbook_db_context': self.context,
            'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
            'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
            'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
            'tc_playbook_out_variables': '',
            'tc_proxy_external': self._to_bool(os.getenv('TC_PROXY_EXTERNAL', 'false')),
            'tc_proxy_host': os.getenv('TC_PROXY_HOST', 'localhost'),
            'tc_proxy_password': os.getenv('TC_PROXY_PASSWORD', ''),
            'tc_proxy_port': os.getenv('TC_PROXY_PORT', '4242'),
            'tc_proxy_tc': self._to_bool(os.getenv('TC_PROXY_TC', 'false')),
            'tc_proxy_username': os.getenv('TC_PROXY_USERNAME', ''),
            'tc_temp_path': os.getenv('TC_TEMP_PATH', 'log'),
        }

    @property
    def install_json(self):
        """Return install.json contents."""
        file_fqpn = os.path.join(self._app_path, 'install.json')
        if self._install_json is None:
            if os.path.isfile(file_fqpn):
                with open(file_fqpn, 'r') as ij_fh:
                    self._install_json = json.load(ij_fh)
            else:
                print('File "{}" could not be found.'.format(file_fqpn))
        return self._install_json

    def input_params(self):
        """Return install.json params in a dict with name param as key.

        Args:
            ij (dict, optional): Defaults to None. The install.json contents.

        Returns:
            dict: A dictionary containing the install.json input params with name as key.
        """
        if self._input_params is None:
            self._input_params = {}
            # TODO: support for projects with multiple install.json files is not supported
            for p in self.install_json.get('params') or []:
                self._input_params.setdefault(p.get('name'), p)
        return self._input_params

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def setup_class(self):
        """Run once before all test cases."""
        self._timer_class_start = time.time()
        self.log.info('{0} {1} {0}'.format('#' * 10, 'Setup Class'))
        self.log.info('[setup class] started: {}'.format(datetime.now().isoformat()))

    def setup_method(self):
        """Run before each test method runs."""
        self._timer_method_start = time.time()
        self._current_test = os.environ.get('PYTEST_CURRENT_TEST').split(' ')[0]
        self.log.info('{0} {1} {0}'.format('=' * 10, self._current_test))
        self.log.info('[setup method] started: {}'.format(datetime.now().isoformat()))
        self.context = os.getenv('TC_PLAYBOOK_DB_CONTEXT', str(uuid.uuid4()))
        self.log.info('[setup method] Context: {}'.format(self.context))
        self.stager.redis.from_dict(self.redis_staging_data)

    @property
    def stager(self):
        """Return instance of Stager class."""
        return Stager(self.tcex(self.default_args), logger)

    def teardown_class(self):
        """Run once before all test cases."""
        self.log.info('{0} {1} {0}'.format('^' * 10, 'Teardown Class'))
        self.log.info(
            '[teardown class] Finished: {}, Elapsed: {}'.format(
                datetime.now().isoformat(), time.time() - self._timer_class_start
            )
        )

    def teardown_method(self):
        """Run after each test method runs."""
        r = self.stager.redis.delete_context(self.context)
        self.log.info('[teardown method] Delete Key Count: {}'.format(r))
        self.log.info(
            '[teardown method] Finished: {}, Elapsed: {}'.format(
                datetime.now().isoformat(), time.time() - self._timer_method_start
            )
        )

    def tcex(self, args):
        """Return an instance of App."""
        try:
            sys.argv.remove('tests')  # remove pytest args
        except ValueError:
            pass
        try:
            sys.argv.remove('-s')  # remove pytest args
        except ValueError:
            pass
        tcex = TcEx()
        app_args = self.default_args
        app_args.update(args)
        tcex.tcex_args.config(app_args)
        return tcex


class TestCasePlaybook(TestCase):
    """Playbook TestCase Class"""

    _output_variables = None

    def output_variables(self, app_id=987):
        """Return playbook output variables"""
        if self._output_variables is None:
            self._output_variables = []
            # TODO: currently there is no support for projects with multiple install.json files.
            for p in self.install_json.get('playbook', {}).get('outputVariables') or []:
                # #App:3313:app.data.count!String
                self._output_variables.append(
                    '#App:{}:{}!{}'.format(app_id, p.get('name'), p.get('type'))
                )
        return self._output_variables

    def run(self, args):  # pylint: disable=too-many-return-statements
        """Run the Playbook App."""
        app = self.app(args)

        # Start
        try:
            app.start()
        except SystemExit as e:
            self.log.error('App failed in start() method ({}).'.format(e))
            return e
        except Exception as err:
            self.log.error('App encountered except in start() method ({}).'.format(err))
            return 1

        # Run
        try:
            if hasattr(app.args, 'tc_action') and app.args.tc_action is not None:
                tc_action = app.args.tc_action
                tc_action_formatted = tc_action.lower().replace(' ', '_')
                tc_action_map = 'tc_action_map'
                if hasattr(app, tc_action):
                    getattr(app, tc_action)()
                elif hasattr(app, tc_action_formatted):
                    getattr(app, tc_action_formatted)()
                elif hasattr(app, tc_action_map):
                    app.tc_action_map.get(app.args.tc_action)()  # pylint: disable=no-member
            else:
                app.run()
        except SystemExit as e:
            self.log.error('App failed in run() method ({}).'.format(e))
            return e
        except Exception as err:
            self.log.error('App encountered except in run() method ({}).'.format(err))
            return 1

        # Write Output
        try:
            app.write_output()
        except SystemExit as e:
            self.log.error('App failed in write_output() method ({}).'.format(e))
            return e
        except Exception as err:
            self.log.error('App encountered except in write_output() method ({}).'.format(err))
            return 1

        # Done
        try:
            app.done()
        except SystemExit as e:
            self.log.error('App failed in done() method ({}).'.format(e))
            return e
        except Exception as err:
            self.log.error('App encountered except in done() method ({}).'.format(err))
            return 1

        return app.tcex.exit_code
