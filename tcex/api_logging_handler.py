""" standard """
# import time
from json import dumps
# from logging import FileHandler, makeLogRecord
from logging import FileHandler

""" third-party """
""" custom """


def create_log_entry(record):
    """Create the API log entry.

    Args:
        record (object): The log entry record.

    Returns:
        (dictionary): The data to log to API
    """
    log_entry = {}

    if hasattr(record, 'created'):
        log_entry['timestamp'] = int(float(record.created) * 1000)

    if hasattr(record, 'msg'):
        log_entry['message'] = record.msg

    if hasattr(record, 'levelname'):
        log_entry['level'] = record.levelname

    return log_entry


class ApiLoggingHandler(FileHandler):
    """Extension of FileHandler

    Sends logs entries to the ThreatConnect API.
    """

    def __init__(self, filename, tcex, max_entries_before_flush=100):
        super(ApiLoggingHandler, self).__init__(filename)
        self._tcex = tcex
        self.max_entries_before_flush = max_entries_before_flush

        # init entries
        self.entries = []

    def emit(self, record):
        """Overload of logger emit method

        Args:
            record (object): The log entry record
        """
        entry = create_log_entry(record)
        self.entries.append(entry)

        # if we've reached the max_entries threshold, flush the handler
        # bcs - would doing a json.dumps and checking size for POST be safer
        #       than an arbitrary amount of events?
        if len(self.entries) > self.max_entries_before_flush:
            self.log_to_api()
            self.entries = []

        super(ApiLoggingHandler, self).emit(record)

    def log_to_api(self):
        """Best effort API logger.

        Send logs to API and do nothing if the attempt fails.

        Example log event::

            [{
                "timestamp": 1478907537000,
                "message": "Test Message",
                "level": "DEBUG"
            }]

        """
        if len(self.entries) > 0:
            # Make API call
            r = self._tcex.request
            r.authorization_method(self._tcex.authorization)
            # bcs - sort entry by *created*?
            # r.body = dumps(self.entries)
            r.body = dumps(self.entries, ensure_ascii=False)
            self.entries = []  # clear entries
            r.http_method = 'POST'
            if self._tcex._args.tc_proxy_tc:
                r.proxies = self._tcex.proxies
            r.url = '{}/v2/logs/app'.format(self._tcex._args.tc_api_path)
            try:
                r.send()
                # results = r.send()
                # if results.headers.get('content-type') == 'application/json':
                #     data = results.json()
                #     if data.get('status') == 'Success':
                #         pass
            except:
                # best effort for now.  don't fret if logging fails
                pass
