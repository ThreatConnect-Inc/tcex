"""ThreatConnect API Logger"""
from logging import FileHandler


def create_log_entry(record):
    """Create the API log entry.

    Args:
        record (object): The log entry record.

    Returns:
        (dictionary): The data to log to API.
    """
    log_entry = {}

    if hasattr(record, 'created'):
        log_entry['timestamp'] = int(float(record.created) * 1000)

    if hasattr(record, 'msg'):
        log_entry['message'] = record.msg

    if hasattr(record, 'levelname'):
        log_entry['level'] = record.levelname

    return log_entry


class TcExLogger(FileHandler):
    """Extension of FileHandler.

    Sends logs entries to the ThreatConnect API.
    """

    def __init__(self, filename, tcex, max_entries_before_flush=100):
        super(TcExLogger, self).__init__(filename)
        self.tcex = tcex
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
        super(TcExLogger, self).emit(record)

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
        if self.entries:
            # Make API call
            try:
                self.tcex.session.post('/v2/logs/app', json=self.entries)
                self.entries = []  # clear entries
            except Exception:
                # best effort on api logging
                pass
