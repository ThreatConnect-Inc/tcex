"""ThreatConnect Batch Import Module."""
# standard library
import gzip
import json
import math
import re
import time
from typing import Optional


class BatchSubmit:
    """ThreatConnect Batch Import Module"""

    def __init__(
        self,
        tcex: object,
        owner: str,
        action: Optional[str] = 'Create',
        attribute_write_type: Optional[str] = 'Replace',
        halt_on_error: Optional[bool] = True,
        playbook_triggers_enabled: Optional[bool] = False,
        tag_write_type: Optional[str] = 'Replace',
        security_label_write_type: Optional[str] = 'Replace',
    ):
        """Initialize Class properties.

        Args:
            tcex: An instance of TcEx object.
            owner: The ThreatConnect owner for Batch action.
            action: Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for Indicator attributes ['Append', 'Replace'].
            halt_on_error: If True any batch error will halt the batch job.
            playbook_triggers_enabled: Enables firing of playbooks.
            security_label_write_type: Write type for labels ['Append', 'Replace'].
            tag_write_type: Write type for tags ['Append', 'Replace'].
        """
        self.tcex = tcex
        self._action = action
        self._attribute_write_type = attribute_write_type
        self._halt_on_error = halt_on_error
        self._owner = owner
        self._playbook_triggers_enabled = playbook_triggers_enabled
        self._security_label_write_type = security_label_write_type
        self._tag_write_type = tag_write_type

        # properties
        self._file_merge_mode = None
        self._hash_collision_mode = None

        # global overrides on batch/file errors
        self._halt_on_batch_error = None
        self._halt_on_poll_error = None

        # default properties
        self._batch_data_count = None
        self._poll_interval = None
        self._poll_interval_times = []
        self._poll_timeout = 3600

    @property
    def _critical_failures(self):  # pragma: no cover
        """Return Batch critical failure messages."""
        return [
            'Encountered an unexpected Exception while processing batch job',
            'would exceed the number of allowed indicators',
        ]

    @property
    def action(self):
        """Return batch action."""
        return self._action

    @action.setter
    def action(self, action):
        """Set batch action."""
        self._action = action

    @property
    def attribute_write_type(self):
        """Return batch attribute write type."""
        return self._attribute_write_type

    @attribute_write_type.setter
    def attribute_write_type(self, write_type: str):
        """Set batch attribute write type."""
        self._attribute_write_type = write_type

    def create_job(self, halt_on_error: Optional[bool] = True) -> int:
        """Submit Batch request to ThreatConnect API.

        Args:
            halt_on_error: If True any exception will raise an error.

        Returns:
            int: The batch id from the API response.
        """
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        try:
            r = self.tcex.session.post('/v2/batch', json=self.settings)
        except Exception as e:
            self.tcex.handle_error(10505, [e], halt_on_error)

        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.handle_error(10510, [r.status_code, r.text], halt_on_error)

        data = r.json()
        if data.get('status') != 'Success':
            self.tcex.handle_error(10510, [r.status_code, r.text], halt_on_error)

        self.tcex.log.debug(f'feature=batch, event=submit-job, status={data}')
        return data.get('data', {}).get('batchId')

    @property
    def error_codes(self):
        """Return static list of Batch error codes and short description"""
        return {
            '0x1001': 'General Error',
            '0x1002': 'Permission Error',
            '0x1003': 'JsonSyntax Error',
            '0x1004': 'Internal Error',
            '0x1005': 'Invalid Indicator Error',
            '0x1006': 'Invalid Group Error',
            '0x1007': 'Item Not Found Error',
            '0x1008': 'Indicator Limit Error',
            '0x1009': 'Association Error',
            '0x100A': 'Duplicate Item Error',
            '0x100B': 'File IO Error',
            '0x2001': 'Indicator Partial Loss Error',
            '0x2002': 'Group Partial Loss Error',
            '0x2003': 'File Hash Merge Error',
        }

    def errors(self, batch_id: int, halt_on_error: Optional[bool] = True) -> list:
        """Retrieve Batch errors to ThreatConnect API.

        .. code-block:: javascript

            [{
                "errorReason": "Incident incident-001 has an invalid status.",
                "errorSource": "incident-001 is not valid."
            }, {
                "errorReason": "Incident incident-002 has an invalid status.",
                "errorSource":"incident-002 is not valid."
            }]

        Args:
            batch_id: The ID returned from the ThreatConnect API for the current batch job.
            halt_on_error: If True any exception will raise an error.

        Returns:
            list: A list of batch errors.
        """
        errors = []
        try:
            self.tcex.log.debug(f'feature=batch, event=retrieve-errors, batch-id={batch_id}')
            r = self.tcex.session.get(f'/v2/batch/{batch_id}/errors')
            # API does not return correct content type
            if r.ok:
                errors = json.loads(r.text)
            # temporarily process errors to find "critical" errors.
            # FR in core to return error codes.
            for error in errors:
                error_reason = error.get('errorReason')
                for error_msg in self._critical_failures:
                    if re.findall(error_msg, error_reason):
                        self.tcex.handle_error(10500, [error_reason], halt_on_error)
        except Exception as e:
            self.tcex.handle_error(560, [e], halt_on_error)

        return errors

    def file_merge_mode(self, value: str) -> None:
        """Set the file merge mode for the entire batch job.

        Args:
            value: A value of Distribute or Merge.
        """
        self._file_merge_mode = value

    @property
    def halt_on_error(self) -> bool:
        """Return batch halt on error setting."""
        return self._halt_on_error

    @halt_on_error.setter
    def halt_on_error(self, halt_on_error: bool):
        """Set batch halt on error setting."""
        self._halt_on_error = halt_on_error

    @property
    def halt_on_batch_error(self) -> bool:
        """Return halt on batch error value."""
        return self._halt_on_batch_error

    @halt_on_batch_error.setter
    def halt_on_batch_error(self, value: bool):
        """Set batch halt on batch error value."""
        if isinstance(value, bool):
            self._halt_on_batch_error = value

    @property
    def halt_on_poll_error(self) -> bool:
        """Return halt on poll error value."""
        return self._halt_on_poll_error

    @halt_on_poll_error.setter
    def halt_on_poll_error(self, value: bool):
        """Set batch halt on poll error value."""
        if isinstance(value, bool):
            self._halt_on_poll_error = value

    def hash_collision_mode(self, value: str):
        """Set the file hash collision mode for the entire batch job.

        Args:
            value: A value of Split, IgnoreIncoming, IgnoreExisting, FavorIncoming,
                and FavorExisting.
        """
        self._hash_collision_mode = value

    def poll(
        self,
        batch_id: int,
        retry_seconds: Optional[int] = None,
        back_off: Optional[float] = None,
        timeout: Optional[int] = None,
        halt_on_error: Optional[bool] = True,
    ) -> dict:
        """Poll Batch status to ThreatConnect API.

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "batchStatus": {
                        "id":3505,
                        "status":"Completed",
                        "errorCount":0,
                        "successCount":0,
                        "unprocessCount":0
                    }
                }
            }

        Args:
            batch_id: The ID returned from the ThreatConnect API for the current batch job.
            retry_seconds: The base number of seconds used for retries when job is not completed.
            back_off: A multiplier to use for backing off on
                each poll attempt when job has not completed.
            timeout: The number of seconds before the poll should timeout.
            halt_on_error: If True any exception will raise an error.

        Returns:
            dict: The batch status returned from the ThreatConnect API.
        """
        # check global setting for override
        if self.halt_on_poll_error is not None:
            halt_on_error = self.halt_on_poll_error

        # initial poll interval
        if self._poll_interval is None and self._batch_data_count is not None:
            # calculate poll_interval base off the number of entries in the batch data
            # with a minimum value of 5 seconds.
            self._poll_interval = max(math.ceil(self._batch_data_count / 300), 5)
        elif self._poll_interval is None:
            # if not able to calculate poll_interval default to 15 seconds
            self._poll_interval = 15

        # poll retry back_off factor
        poll_interval_back_off = float(2.5 if back_off is None else back_off)

        # poll retry seconds
        poll_retry_seconds = int(5 if retry_seconds is None else retry_seconds)

        # poll timeout
        if timeout is None:
            timeout = self.poll_timeout
        else:
            timeout = int(timeout)
        params = {'includeAdditional': 'true'}

        poll_count = 0
        poll_time_total = 0
        data = {}
        while True:
            poll_count += 1
            poll_time_total += self._poll_interval
            time.sleep(self._poll_interval)
            self.tcex.log.info(f'feature=batch, event=progress, poll-time={poll_time_total}')
            try:
                # retrieve job status
                r = self.tcex.session.get(f'/v2/batch/{batch_id}', params=params)
                if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                    self.tcex.handle_error(545, [r.status_code, r.text], halt_on_error)
                    return data
                data = r.json()
                if data.get('status') != 'Success':
                    self.tcex.handle_error(545, [r.status_code, r.text], halt_on_error)
            except Exception as e:
                self.tcex.handle_error(540, [e], halt_on_error)

            if data.get('data', {}).get('batchStatus', {}).get('status') == 'Completed':
                # store last 5 poll times to use in calculating average poll time
                modifier = poll_time_total * 0.7
                self._poll_interval_times = self._poll_interval_times[-4:] + [modifier]

                weights = [1]
                poll_interval_time_weighted_sum = 0
                for poll_interval_time in self._poll_interval_times:
                    poll_interval_time_weighted_sum += poll_interval_time * weights[-1]
                    # weights will be [1, 1.5, 2.25, 3.375, 5.0625] for all 5 poll times depending
                    # on how many poll times are available.
                    weights.append(weights[-1] * 1.5)

                # pop off the last weight so its not added in to the sum
                weights.pop()

                # calculate the weighted average of the last 5 poll times
                self._poll_interval = math.floor(poll_interval_time_weighted_sum / sum(weights))

                if poll_count == 1:
                    # if completed on first poll, reduce poll interval.
                    self._poll_interval = self._poll_interval * 0.85

                self.tcex.log.debug(f'feature=batch, poll-time={poll_time_total}, status={data}')
                return data

            # update poll_interval for retry with max poll time of 20 seconds
            self._poll_interval = min(
                poll_retry_seconds + int(poll_count * poll_interval_back_off), 20
            )

            # time out poll to prevent App running indefinitely
            if poll_time_total >= timeout:
                self.tcex.handle_error(550, [timeout], True)

    @property
    def poll_timeout(self) -> int:
        """Return current poll timeout value."""
        return self._poll_timeout

    @poll_timeout.setter
    def poll_timeout(self, seconds: int):
        """Set the poll timeout value."""
        self._poll_timeout = int(seconds)

    @property
    def security_label_write_type(self):
        """Return batch security label write type."""
        return self._security_label_write_type

    @security_label_write_type.setter
    def security_label_write_type(self, write_type: str):
        """Set batch security label write type."""
        self._security_label_write_type = write_type

    @property
    def settings(self) -> dict:
        """Return batch job settings."""
        _settings = {
            'action': self._action,
            'attributeWriteType': self.attribute_write_type,
            'haltOnError': str(self._halt_on_error).lower(),
            'owner': self._owner,
            'playbookTriggersEnabled': str(self._playbook_triggers_enabled).lower(),
            'securityLabelWriteType': self.security_label_write_type,
            'tagWriteType': self.tag_write_type,
            'version': 'V2',
        }
        if self._hash_collision_mode is not None:
            _settings['hashCollisionMode'] = self._hash_collision_mode
        if self._file_merge_mode is not None:
            _settings['fileMergeMode'] = self._file_merge_mode
        return _settings

    def submit(self, batch_filename: str, halt_on_error: Optional[bool] = True) -> dict:
        """Submit Batch request to ThreatConnect API.

        Args:
            batch_filename: The filename for the batch JSON file.
            halt_on_error: If True the process should halt if any errors are encountered.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        content = gzip.open(batch_filename, 'rt').read()

        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        # store the length of the batch data to use for poll interval calculations
        self.tcex.log.info(
            '''feature=batch, event=submit-create-and-upload, type=group, '''
            f'''count={len(content.get('group')):,}'''
        )
        self.tcex.log.info(
            '''feature=batch, event=submit-create-and-upload, type=indicator, '''
            f'''count={len(content.get('indicator')):,}'''
        )

        files = (('config', json.dumps(self.settings)), ('content', json.dumps(content)))
        params = {'includeAdditional': 'true'}
        try:
            r = self.tcex.session.post('/v2/batch/createAndUpload', files=files, params=params)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(10510, [r.status_code, r.text], halt_on_error)
            return r.json()
        except Exception as e:
            self.tcex.handle_error(10505, [e], halt_on_error)

        return {}

    def submit_data(
        self, batch_id: int, content: dict, halt_on_error: Optional[bool] = True
    ) -> dict:
        """Submit Batch request to ThreatConnect API.

        Args:
            batch_id: The batch id of the current job.
            content: The dict of groups and indicator data.
            halt_on_error (Optional[bool] = True): If True the process
                should halt if any errors are encountered.

        Returns:
            dict: The response data
        """
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        # store the length of the batch data to use for poll interval calculations
        # self._batch_data_count = len(content.get('group')) + len(content.get('indicator'))
        # self.tcex.log.info(
        #     f'feature=batch, action=submit-data, batch-size={self._batch_data_count:,}'
        # )

        headers = {'Content-Type': 'application/octet-stream'}
        try:
            r = self.tcex.session.post(f'/v2/batch/{batch_id}', headers=headers, data=content)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(10525, [r.status_code, r.text], halt_on_error)
            return r.json()
        except Exception as e:
            self.tcex.handle_error(10520, [e], halt_on_error)

        return None

    @property
    def tag_write_type(self):
        """Return batch tag write type."""
        return self._tag_write_type

    @tag_write_type.setter
    def tag_write_type(self, write_type: str):
        """Set batch tag write type."""
        self._tag_write_type = write_type

    # def write_error_json(self, errors: list) -> None:
    #     """Write the errors to a JSON file for debuging purposes.

    #     Args:
    #         errors: A list of errors to write out.
    #     """
    #     if self.debug:
    #         if not errors:
    #             errors = []
    #         # get timestamp as a string without decimal place and consistent length
    #         timestamp = str(round(time.time() * 10000000))
    #         error_json_file = os.path.join(self.debug_path_batch, f'errors-{timestamp}.json.gz')
    #         with gzip.open(error_json_file, mode='wt', encoding='utf-8') as fh:
    #             json.dump(errors, fh)
