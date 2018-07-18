# -*- coding: utf-8 -*-
""" TcEx Common Arg Handler """
from argparse import ArgumentParser


class TcExArgParser(ArgumentParser):
    """Overload of the ArgumentParser class.

    Adding common arguments for TcEx apps.
    """

    def __init__(self, **kwargs):
        """Initialize the Class properties."""
        super(TcExArgParser, self).__init__(**kwargs)
        # batch defaults
        self._batch_action = 'Create'
        self._batch_chunk = 25000
        self._batch_halt_on_error = False
        self._batch_poll_interval = 15
        self._batch_poll_interval_max = 3600
        self._batch_write_type = 'Append'

        # playbook defaults
        self._tc_playbook_db_type = 'Redis'
        self._tc_playbook_db_context = '1234-abcd'
        self._tc_playbook_db_path = 'localhost'
        self._tc_playbook_db_port = '6379'

        # standard defaults
        self._tc_api_path = 'https://api.threatconnect.com'
        self._tc_in_path = '/tmp'
        self._tc_log_file = 'app.log'
        self._tc_log_path = '/tmp'
        self._tc_out_path = '/tmp'
        self._tc_secure_params = False
        self._tc_temp_path = '/tmp'
        self._tc_user_id = None
        self._tc_log_to_api = False
        self._tc_log_level = 'info'

        # include arguments
        self._api_arguments()
        self._batch_arguments()
        self._playbook_arguments()
        self._standard_arguments()

    def _api_arguments(self):
        """Argument specific to working with TC API.

        --tc_token token                  Token provided by ThreatConnect for app Authorization.
        --tc_token_expires token_expires  Expiration time for the passed Token.
        --api_access_id access_id         Access ID used for HMAC Authorization.
        --api_secret_key secret_key       Secret Key used for HMAC Authorization.
        """

        # TC main >= 4.4 token will be passed to jobs.
        self.add_argument(
            '--tc_token', default=None, help='ThreatConnect API Token')
        self.add_argument(
            '--tc_token_expires', default=None,
            help='ThreatConnect API Token Expiration Time', type=int)

        # TC Integrations Server or TC main < 4.4
        self.add_argument(
            '--api_access_id', default=None, help='ThreatConnect API Access ID', required=False)
        self.add_argument(
            '--api_secret_key', default=None, help='ThreatConnect API Secret Key', required=False)

        # Validate ThreatConnect SSL certificate
        self.add_argument(
            '--tc_verify', action='store_true', help='Validate the ThreatConnect SSL Cert')

    def _batch_arguments(self):
        """Arguments specific to Batch API writes.

        --batch_action action          Action for the batch job ['Create', 'Delete'].
        --batch_chunk number           The maximum number of indicator per batch job.
        --batch_halt_on_error          Flag to indicate that the batch job should halt on error.
        --batch_poll_interval seconds  Seconds between batch status polls.
        --batch_interval_max seconds   Seconds before app should time out waiting on batch job
                                       completion.
        --batch_write_type type        Write type for Indicator attributes ['Append', 'Replace'].
        """

        self.add_argument(
            '--batch_action', choices=['Create', 'Delete'], default=self._batch_action,
            help='Action for the batch job')
        self.add_argument(
            '--batch_chunk', default=self._batch_chunk,
            help='Max number of indicators per batch', type=int)
        self.add_argument(
            '--batch_halt_on_error', action='store_true', default=self._batch_halt_on_error,
            help='Halt batch job on error')
        self.add_argument(
            '--batch_poll_interval', default=self._batch_poll_interval,
            help='Frequency to run status check for batch job.', type=int)
        self.add_argument(
            '--batch_poll_interval_max', default=self._batch_poll_interval_max,
            help='Maximum amount of time for status check on batch job.', type=int)
        self.add_argument(
            '--batch_write_type', choices=['Append', 'Replace'], default=self._batch_write_type,
            help='Append or Replace attributes.')

    def _playbook_arguments(self):
        """Argument specific to playbook apps.

        These arguments will be passed to every playbook app by default.

        --tc_playbook_db_type type        The DB type (currently on Redis is supported).
        --tc_playbook_db_context context  The playbook context provided by TC.
        --tc_playbook_db_path path        The DB path or server name.
        --tc_playbook_db_port port        The DB port when required.
        --tc_playbook_out_variables vars  The output variable requested by downstream apps.
        """

        self.add_argument(
            '--tc_playbook_db_type', default=self._tc_playbook_db_type,
            help='Playbook DB type')
        self.add_argument(
            '--tc_playbook_db_context', default=self._tc_playbook_db_context,
            help='Playbook DB Context')
        self.add_argument(
            '--tc_playbook_db_path', default=self._tc_playbook_db_path,
            help='Playbook DB path')
        self.add_argument(
            '--tc_playbook_db_port', default=self._tc_playbook_db_port,
            help='Playbook DB port')
        self.add_argument(
            '--tc_playbook_out_variables', help='Playbook output variables', required=False)

    def _standard_arguments(self):
        """These are the standard args passed to every TcEx App.

        --api_default_org org        The TC API user default organization.
        --tc_api_path path           The TC API path (e.g https://api.threatconnect.com).
        --tc_in_path path            The app in path.
        --tc_log_file filename       The app log file name.
        --tc_log_path path           The app log path.
        --tc_out_path path           The app out path.
        --tc_secure_params bool      Flag to indicator secure params is supported.
        --tc_temp_path path          The app temp path.
        --tc_user_id id              The user id of user running the job.

        --tc_proxy_host host         The proxy host.
        --tc_proxy_port port         The proxy port.
        --tc_proxy_username user     The proxy username.
        --tc_proxy_password pass     The proxy password.
        --tc_proxy_external          Flag to indicate external communications requires the use of a
                                     proxy.
        --tc_proxy_tc                Flag to indicate TC communications requires the use of a proxy.
        --tc_log_to_api              Flag to indicate that app should log to API.
        --tc_log_level               The logging level for the app.
        --logging level              Alias for **tc_log_level**.
        """

        self.add_argument(
            '--api_default_org', default=None, help='ThreatConnect api default Org')
        self.add_argument(
            '--tc_action_channel', default=None, help='ThreatConnect AOT action channel')
        self.add_argument(
            '--tc_aot_enabled', action='store_true', help='ThreatConnect AOT enabled')
        self.add_argument(
            '--tc_api_path', default=self._tc_api_path, help='ThreatConnect api path')
        self.add_argument(
            '--tc_exit_channel', default=None, help='ThreatConnect AOT exit channel')
        self.add_argument(
            '--tc_in_path', default=self._tc_in_path, help='ThreatConnect in path')
        self.add_argument(
            '--tc_log_file', default=self._tc_log_file, help='App logfile name')
        self.add_argument(
            '--tc_log_path', default=self._tc_log_path, help='ThreatConnect log path')
        self.add_argument(
            '--tc_out_path', default=self._tc_out_path, help='ThreatConnect output path')
        self.add_argument(
            '--tc_secure_params', action='store_true', default=self._tc_secure_params,
            help='ThreatConnect Secure params enabled')
        self.add_argument(
            '--tc_terminate_seconds', default=None, help='ThreatConnect AOT terminate seconds',
            type=int)
        self.add_argument(
            '--tc_temp_path', default=self._tc_temp_path, help='ThreatConnect temp path')
        self.add_argument(
            '--tc_user_id', default=self._tc_user_id, help='User ID')

        # Proxy Configuration
        self.add_argument(
            '--tc_proxy_host', default=None, help='Proxy Host')
        self.add_argument(
            '--tc_proxy_port', default=None, help='Proxy Port')
        self.add_argument(
            '--tc_proxy_username', default=None, help='Proxy User')
        self.add_argument(
            '--tc_proxy_password', default=None, help='Proxy Password')
        self.add_argument(
            '--tc_proxy_external', '--apply_proxy_external', action='store_true', default=False,
            help='Proxy External Connections', dest='tc_proxy_external')
        self.add_argument(
            '--tc_proxy_tc', '--apply_proxy_tc', action='store_true', default=False,
            help='Proxy TC Connection', dest='tc_proxy_tc')

        #
        # Logging
        #

        # currently only applicable to TC Main
        self.add_argument(
            '--tc_log_to_api', action='store_true', default=self._tc_log_to_api,
            help='ThreatConnect API Logging')
        # self.add_argument(
        #     '--tc_log_level', '--logging', choices=['debug', 'info', 'warning', 'error',
        #     'critical'],
        #     default=self._tc_log_level, help='Logging Level', dest='tc_log_level', type=str.lower)
        # BCS - temporarily until there is some way to configure App logging level in the UI
        self.add_argument(
            '--logging', choices=['debug', 'info', 'warning', 'error', 'critical'],
            default=None, help='Logging Level', dest='logging', type=str.lower)
        self.add_argument(
            '--tc_log_level', choices=['debug', 'info', 'warning', 'error', 'critical'],
            default=None, help='Logging Level', dest='tc_log_level', type=str.lower)
