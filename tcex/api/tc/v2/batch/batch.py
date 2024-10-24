"""TcEx Framework Module"""

# standard library
import gzip
import json
import os
import shelve  # nosec
import sys
import threading
import time
import traceback
from collections import deque
from collections.abc import Callable
from typing import Any

# third-party
from requests import Response, Session

# first-party
from tcex.api.tc.v2.batch.batch_submit import BatchSubmit
from tcex.api.tc.v2.batch.batch_writer import BatchWriter, GroupType, IndicatorType
from tcex.exit.error_code import handle_error
from tcex.input.input import Input


class Batch(BatchWriter, BatchSubmit):
    """ThreatConnect Batch Import Module

    Args:
        inputs: The App inputs.
        session_tc: The ThreatConnect API session.
        owner: The ThreatConnect owner for Batch action.
        action: Action for the batch job ['Create', 'Delete'].
        attribute_write_type: Write type for attributes ['Append', 'Replace'].
        halt_on_error: If True, any batch error will halt the batch job.
        playbook_triggers_enabled: If True, Playbook will be triggered when TI data is created.
        security_label_write_type: Write type for labels ['Append', 'Replace'].
        tag_write_type: Write type for tags ['Append', 'Replace'].
    """

    def __init__(
        self,
        inputs: Input,
        session_tc: Session,
        owner: str,
        action: str = 'Create',
        attribute_write_type: str = 'Replace',
        halt_on_error: bool = True,
        playbook_triggers_enabled: bool = False,
        tag_write_type: str = 'Replace',
        security_label_write_type: str = 'Replace',
    ):
        """Initialize instance properties."""
        BatchWriter.__init__(self, inputs=inputs, session_tc=session_tc, output_dir='')
        BatchSubmit.__init__(
            self,
            inputs=inputs,
            session_tc=session_tc,
            owner=owner,
            action=action,
            attribute_write_type=attribute_write_type,
            halt_on_error=halt_on_error,
            playbook_triggers_enabled=playbook_triggers_enabled,
            tag_write_type=tag_write_type,
            security_label_write_type=security_label_write_type,
        )

        self._action = action
        self._attribute_write_type = attribute_write_type
        self._halt_on_error = halt_on_error
        self._owner = owner
        self._playbook_triggers_enabled = playbook_triggers_enabled
        self._security_label_write_type = security_label_write_type
        self._tag_write_type = tag_write_type

        # properties
        self._batch_max_chunk = 5_000
        self._batch_max_size = 75_000_000  # max size in bytes
        self._file_merge_mode = None
        self._file_threads = []
        self._hash_collision_mode = None
        self._submit_thread = None

        # global overrides on batch/file errors
        self._halt_on_batch_error = None
        self._halt_on_file_error = None
        self._halt_on_poll_error = None

        # debug/saved flags
        self._saved_xids = None
        self._saved_groups = None  # indicates groups shelf file was provided
        self._saved_indicators = None  # indicates indicators shelf file was provided
        self.enable_saved_file = False

        # default properties
        self._batch_data_count = None
        self._poll_interval = None
        self._poll_interval_times = []
        self._poll_timeout = 3600

        # batch debug/replay variables
        self._debug = None
        self.debug_path = os.path.join(self.inputs.model.tc_temp_path, 'DEBUG')
        self.debug_path_batch = os.path.join(self.debug_path, 'batch_data')
        self.debug_path_group_shelf = os.path.join(self.debug_path, 'groups-saved')
        self.debug_path_indicator_shelf = os.path.join(self.debug_path, 'indicators-saved')
        self.debug_path_files = os.path.join(self.debug_path, 'batch_files')
        self.debug_path_xids = os.path.join(self.debug_path, 'xids-saved')

    def _group(self, group_data: dict | GroupType, store: bool = True) -> dict | GroupType:
        """Return previously stored group or new group.

        Args:
            group_data: An Group dict or instance of GroupType.
            store: If True the group data will be stored in instance list.

        Returns:
            (dict|GroupType): The new Group dict/GroupType or the previously stored dict/GroupType.
        """
        if store is False:
            return group_data

        if isinstance(group_data, dict):
            # get xid from dict
            xid = group_data['xid']
        else:
            # get xid from GroupType
            xid = group_data.xid

        if self.groups.get(xid) is not None:
            # return existing group from memory
            group_data = self.groups[xid]
        elif self.groups_shelf.get(xid) is not None:
            # return existing group from shelf
            group_data = self.groups_shelf[xid]
        else:
            # store new group
            self.groups[xid] = group_data
        return group_data

    def _indicator(
        self, indicator_data: dict | IndicatorType, store: bool = True
    ) -> dict | IndicatorType:
        """Return previously stored indicator or new indicator.

        Args:
            indicator_data: An Indicator dict or instance of IndicatorType.
            store: If True the indicator data will be stored in instance list.
        """
        if store is False:
            return indicator_data

        if isinstance(indicator_data, dict):
            # get xid from dict
            xid = indicator_data['xid']
        else:
            # get xid from IndicatorType
            xid = indicator_data.xid

        if self.indicators.get(xid) is not None:
            # return existing indicator from memory
            indicator_data = self.indicators[xid]
        elif self.indicators_shelf.get(xid) is not None:
            # return existing indicator from shelf
            indicator_data = self.indicators_shelf[xid]
        else:
            # store new indicators
            self.indicators[xid] = indicator_data
        return indicator_data

    def close(self):
        """Cleanup batch job."""
        # allow pol thread to complete before wrapping up
        if self._submit_thread and hasattr(self._submit_thread, 'is_alive'):
            self._submit_thread.join()

        # allow file threads to complete before wrapping up job
        for t in self._file_threads:
            t.join()

        self.groups_shelf.close()
        self.indicators_shelf.close()
        if not self.debug and not self.enable_saved_file:
            # delete saved files
            if os.path.isfile(self.group_shelf_fqfn):
                os.remove(self.group_shelf_fqfn)
            if os.path.isfile(self.group_shelf_fqfn):
                os.remove(self.indicator_shelf_fqfn)

    @property
    def data(self) -> dict:
        """Return the batch indicator/group and file data to be sent to the ThreatConnect API.

        **Processing Order:**
        * Process groups in memory up to max batch size.
        * Process groups in shelf to max batch size.
        * Process indicators in memory up to max batch size.
        * Process indicators in shelf up to max batch size.

        This method will remove the group/indicator from memory and/or shelf.

        Returns:
            dict: A dictionary of group, indicators, and/or file data.
        """
        data = {'file': {}, 'group': [], 'indicator': []}
        tracker = {'count': 0, 'bytes': 0}

        # process group from memory, returning if max values have been reached
        if self.data_groups(data, self.groups, tracker) is True:
            return data

        # process group from shelf file, returning if max values have been reached
        if self.data_groups(data, self.groups_shelf, tracker) is True:
            return data

        # process indicator from memory, returning if max values have been reached
        if self.data_indicators(data, self.indicators, tracker) is True:
            return data

        # process indicator from shelf file, returning if max values have been reached
        if self.data_indicators(data, self.indicators_shelf, tracker) is True:
            return data

        return data

    def data_group_association(self, data: dict, tracker: dict, xid: str):
        """Return group dict array following all associations.

        The *data* dict is passed by reference to make it easier to update both the group data
        and file data inline versus passing the data all the way back up to the calling methods.

        Args:
            data: The data dict to update with group and file data.
            tracker: A dict containing total count of all entities collected and
                the total size in bytes of all entities collected.
            xid: The xid of the group to retrieve associations.
        """
        xids = deque()
        xids.append(xid)

        while xids:
            xid = xids.popleft()  # remove current xid
            group_data = None

            if xid in self.groups:
                group_data = self.groups.get(xid)
                del self.groups[xid]
            elif xid in self.groups_shelf:
                group_data = self.groups_shelf.get(xid)
                del self.groups_shelf[xid]

            if group_data:
                file_data, group_data = self.data_group_type(group_data)
                data['group'].append(group_data)
                if file_data:
                    data['file'][xid] = file_data

                # update entity trackers
                tracker['count'] += 1
                tracker['bytes'] += sys.getsizeof(json.dumps(group_data))

                # extend xids with any groups associated with the same GroupType
                xids.extend(group_data.get('associatedGroupXid', []))

    @staticmethod
    def data_group_type(group_data: dict | GroupType) -> tuple[dict, dict]:
        """Return dict representation of group data and file data.

        Args:
            group_data: The group data dict or GroupType.

        Returns:
            Tuple[dict, dict]: A tuple containing file_data and group_data.
        """
        file_data = {}
        if isinstance(group_data, dict):
            # process file content
            file_content = group_data.pop('fileContent', None)
            if file_content is not None:
                file_data = {
                    'fileContent': file_content,
                    'fileName': group_data.get('fileName'),
                    'type': group_data.get('type'),
                }
        else:
            # get the file data from the GroupType and return dict format of GroupType
            if group_data.data.get('type') in ['Document', 'Report']:
                file_data = group_data.file_data
            group_data = group_data.data

        return file_data, group_data

    def data_groups(self, data: dict, groups: dict | shelve.Shelf[Any], tracker: dict) -> bool:
        """Process Group data.

        Args:
            data: The data dict to update with group and file data.
            groups: The list of groups to process.
            tracker: A dict containing total count of all entities collected and
                the total size in bytes of all entities collected.

        Returns:
            bool: True if max values have been hit, else False.
        """
        # convert groups.keys() to a list to prevent dictionary change error caused by
        # the data_group_association function deleting items from the GroupType.

        # process the group
        for xid in list(groups.keys()):
            # get association from group data
            self.data_group_association(data, tracker, xid)

            if tracker['count'] % 2_500 == 0:
                # log count/size at a sane level
                self.log.info(
                    '''feature=batch, action=data-groups, '''
                    f'''count={tracker.get('count'):,}, bytes={tracker.get('bytes'):,}'''
                )

            if (
                tracker['count'] >= self._batch_max_chunk
                or tracker['bytes'] >= self._batch_max_size
            ):
                # stop processing xid once max limit are reached
                self.log.info(
                    '''feature=batch, event=max-value-reached, '''
                    f'''count={tracker.get('count'):,}, bytes={tracker.get('bytes'):,}'''
                )
                return True
        return False

    def data_indicators(
        self, data: dict, indicators: dict | shelve.Shelf[Any], tracker: dict
    ) -> bool:
        """Process Indicator data.

        Args:
            data: The data dict to update with group and file data.
            indicators: The list of indicators to process.
            tracker: A dict containing total count of all entities collected and
                the total size in bytes of all entities collected.

        Returns:
            bool: True if max values have been hit, else False.
        """
        # process the indicators
        for xid, indicator_data in list(indicators.items()):
            if not isinstance(indicator_data, dict):
                indicator_data = indicator_data.data
            data['indicator'].append(indicator_data)
            del indicators[xid]

            # update entity trackers
            tracker['count'] += 1
            tracker['bytes'] += sys.getsizeof(json.dumps(indicator_data))

            if tracker['count'] % 2_500 == 0:
                # log count/size at a sane level
                self.log.info(
                    '''feature=batch, action=data-indicators, '''
                    f'''count={tracker.get('count'):,}, bytes={tracker.get('bytes'):,}'''
                )

            if (
                tracker['count'] >= self._batch_max_chunk
                or tracker['bytes'] >= self._batch_max_size
            ):
                # stop processing xid once max limit are reached
                self.log.info(
                    '''feature=batch, event=max-value-reached, '''
                    f'''count={tracker.get('count'):,}, bytes={tracker.get('bytes'):,}'''
                )
                return True
        return False

    @property
    def debug(self):
        """Return debug setting"""
        if self._debug is None:
            self._debug = False

            # switching DEBUG file to a directory
            if os.path.isfile(self.debug_path):
                os.remove(self.debug_path)
                os.makedirs(self.debug_path, exist_ok=True)

            if os.path.isdir(self.debug_path) and os.access(self.debug_path, os.R_OK):
                # create directories only required when debug is enabled
                # batch_json - store the batch*.json files
                # documents - store the file downloads (e.g., *.pdf)
                # reports - store the file downloads (e.g., *.pdf)
                os.makedirs(self.debug_path, exist_ok=True)
                os.makedirs(self.debug_path_batch, exist_ok=True)
                os.makedirs(self.debug_path_files, exist_ok=True)
                self._debug = True
        return self._debug

    @property
    def halt_on_file_error(self) -> bool:
        """Return halt on file post error value."""
        return self._halt_on_file_error or False

    @halt_on_file_error.setter
    def halt_on_file_error(self, value: bool):
        """Set halt on file post error value."""
        if isinstance(value, bool):
            self._halt_on_file_error = value

    def process_all(self, process_files: bool = True):
        """Process Batch request to ThreatConnect API.

        Args:
            process_files: Send any document or report attachments to the API.
        """
        while True:
            content = self.data
            file_data = content.pop('file', {})
            if not content.get('group') and not content.get('indicator'):
                break

            # special code for debugging App using batchV2.
            self.write_batch_json(content)

            # store the length of the batch data to use for poll interval calculations
            self.log.info(
                '''feature=batch, event=process-all, type=group, '''
                f'''count={len(content['group']):,}'''
            )
            self.log.info(
                '''feature=batch, event=process-all, type=indicator, '''
                f'''count={len(content['indicator']):,}'''
            )

        if process_files:
            self.process_files(file_data)

    def process_files(self, file_data: dict):
        """Process Files for Documents and Reports to ThreatConnect API.

        Args:
            file_data: The file data to be processed.
        """
        for xid, content_data in list(file_data.items()):
            del file_data[xid]  # win or loose remove the entry

            # define the saved filename
            api_branch = 'documents' if content_data.get('type') == 'Report' else 'reports'
            fqfn = os.path.join(
                self.debug_path_files,
                f'''{api_branch}--{xid}--{content_data.get('fileName').replace('/', ':')}''',
            )

            # used for debug/testing to prevent upload of previously uploaded file
            if self.debug and xid in self.saved_xids:
                self.log.debug(
                    f'feature=batch-submit-files, action=skip-previously-saved-file, xid={xid}'
                )
                continue

            if os.path.isfile(fqfn):
                self.log.debug(
                    f'feature=batch-submit-files, action=skip-previously-saved-file, xid={xid}'
                )
                continue

            # process the file content
            content = content_data.get('fileContent')
            if callable(content):
                content_callable_name = getattr(content, '__name__', repr(content))
                self.log.trace(
                    f'feature=batch-submit-files, method={content_callable_name}, xid={xid}'
                )
                content = content_data.get('fileContent')(xid)

            if content is None:
                self.log.warning(f'feature=batch-submit-files, xid={xid}, event=content-null')
                continue

            # write the file to disk
            with open(fqfn, 'wb') as fh:
                fh.write(content)

    @property
    def saved_groups(self) -> bool:
        """Return True if saved group files exits, else False."""
        if self._saved_groups is None:
            self._saved_groups = False
            if (
                self.enable_saved_file
                and os.path.isfile(self.debug_path_group_shelf)
                and os.access(self.debug_path_group_shelf, os.R_OK)
            ):
                self._saved_groups = True
                self.log.debug('feature=batch, event=saved-groups-file-found')
        return self._saved_groups

    @property
    def saved_indicators(self) -> bool:
        """Return True if saved indicators files exits, else False."""
        if self._saved_indicators is None:
            self._saved_indicators = False
            if (
                self.enable_saved_file
                and os.path.isfile(self.debug_path_indicator_shelf)
                and os.access(self.debug_path_indicator_shelf, os.R_OK)
            ):
                self._saved_indicators = True
                self.log.debug('feature=batch, event=saved-indicator-file-found')
        return self._saved_indicators

    @property
    def saved_xids(self) -> list:
        """Return previously saved xids."""
        if self._saved_xids is None:
            self._saved_xids = []
            if self.debug:
                if os.path.isfile(self.debug_path_xids) and os.access(
                    self.debug_path_xids, os.R_OK
                ):
                    with open(self.debug_path_xids) as fh:
                        self._saved_xids = fh.read().splitlines()
        return self._saved_xids

    @saved_xids.setter
    def saved_xids(self, xid: str):
        """Append xid to xids saved file."""
        with open(self.debug_path_xids, 'a') as fh:
            fh.write(f'{xid}\n')

    def submit(  # pylint: disable=arguments-differ, arguments-renamed
        self,
        poll: bool = True,
        errors: bool = True,
        process_files: bool = True,
        halt_on_error: bool = True,
    ) -> dict:
        """Submit Batch request to ThreatConnect API.

        By default this method will submit the job request and data and if the size of the data
        is below the value **synchronousBatchSaveLimit** set in System Setting it will process
        the request synchronously and return the batch status.  If the size of the batch is greater
        than the value set the batch job will be queued.
        Errors are not retrieve automatically and need to be enabled.

        If any of the submit, poll, or error methods fail the entire submit will halt at the point
        of failure. The behavior can be changed by setting halt_on_error to False.

        Each of these methods can also be called on their own for greater control of the submit
        process.

        Args:
            poll: If True poll batch for status.
            errors: If True retrieve any batch errors (only if poll is True).
            process_files: If true send any document or report attachments to the API.
            halt_on_error: If True any exception will raise an error.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        # get file, group, and indicator data
        content = self.data

        # pop any file content to pass to submit_files
        file_data = content.pop('file', {})
        batch_data = (
            self.submit_create_and_upload(content=content, halt_on_error=halt_on_error)
            .get('data', {})
            .get('batchStatus', {})
        )
        batch_id = batch_data.get('id')
        if batch_id is not None:
            self.log.info(f'feature=batch, event=submit, batch-id={batch_id}')
            # job hit queue
            if poll:
                # poll for status
                batch_data = (
                    self.poll(batch_id=batch_id, halt_on_error=halt_on_error)
                    .get('data', {})
                    .get('batchStatus', {})
                )
                if errors:
                    # retrieve errors
                    error_groups = batch_data.get('errorGroupCount', 0)
                    error_indicators = batch_data.get('errorIndicatorCount', 0)
                    if error_groups > 0 or error_indicators > 0:
                        batch_data['errors'] = self.errors(batch_id)
            else:
                # can't process files if status is unknown (polling must be enabled)
                process_files = False

        if process_files:
            # submit file data after batch job is complete
            self._file_threads.append(
                self.submit_thread(
                    name='submit-files',
                    target=self.submit_files,
                    args=(
                        file_data,
                        halt_on_error,
                    ),
                )
            )
        return batch_data

    def submit_all(
        self,
        poll: bool = True,
        errors: bool = True,
        process_files: bool = True,
        halt_on_error: bool = True,
    ) -> list[dict]:
        """Submit Batch request to ThreatConnect API.

        By default this method will submit the job request and data and if the size of the data
        is below the value **synchronousBatchSaveLimit** set in System Setting it will process
        the request synchronously and return the batch status.  If the size of the batch is greater
        than the value set the batch job will be queued.
        Errors are not retrieve automatically and need to be enabled.

        If any of the submit, poll, or error methods fail the entire submit will halt at the point
        of failure. The behavior can be changed by setting halt_on_error to False.

        Each of these methods can also be called on their own for greater control of the submit
        process.

        Args:
            poll: If True poll batch for status.
            errors: If True retrieve any batch errors (only if poll is True).
            process_files: If true send any document or report attachments to the API.
            halt_on_error: If True any exception will raise an error.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        batch_data_array = []
        file_data = {}
        while True:
            batch_data: dict[str, int | list | str] | None = {}
            batch_id: int | None = None

            # get file, group, and indicator data
            content = self.data

            # break loop when end of data is reached
            if not content.get('group') and not content.get('indicator'):
                break

            if self.action.lower() == 'delete':
                # no need to process files on a delete batch job
                process_files = False

                # while waiting of FR for delete support in createAndUpload submit delete request
                # the old way (submit job + submit data), still using V2.
                if len(content) > 0:  # pylint: disable=len-as-condition
                    batch_id = self.submit_job(halt_on_error)
                    if batch_id is not None:
                        batch_data = self.submit_data(
                            batch_id=batch_id, content=content, halt_on_error=halt_on_error
                        )
                else:
                    batch_data = {}
            else:
                # pop any file content to pass to submit_files
                file_data = content.pop('file', {})
                batch_data = (
                    self.submit_create_and_upload(content=content, halt_on_error=halt_on_error)
                    .get('data', {})
                    .get('batchStatus', {})
                )
                batch_id = batch_data.get('id')  # type: ignore

            if batch_id is not None:
                self.log.info(f'feature=batch, event=status, batch-id={batch_id}')
                # job hit queue
                if poll:
                    # poll for status
                    batch_data = (
                        self.poll(batch_id, halt_on_error=halt_on_error)
                        .get('data', {})
                        .get('batchStatus', {})
                    )
                    if errors and batch_data is not None:
                        # retrieve errors
                        error_count = batch_data.get('errorCount', 0)
                        error_groups = batch_data.get('errorGroupCount', 0)
                        error_indicators = batch_data.get('errorIndicatorCount', 0)
                        if (
                            isinstance(error_count, int)
                            and isinstance(error_groups, int)
                            and isinstance(error_indicators, int)
                        ):
                            if error_count > 0 or error_groups > 0 or error_indicators > 0:
                                batch_data['errors'] = self.errors(batch_id)
                else:
                    # can't process files if status is unknown (polling must be enabled)
                    process_files = False

            if process_files:
                # submit file data after batch job is complete
                self._file_threads.append(
                    self.submit_thread(
                        name='submit-files',
                        target=self.submit_files,
                        args=(
                            file_data,
                            halt_on_error,
                        ),
                    )
                )
            batch_data_array.append(batch_data)

            # write errors for debugging
            if isinstance(batch_data, dict):
                batch_errors = batch_data.get('errors', [])
                if isinstance(batch_errors, list) and len(batch_errors) > 0:
                    self.write_error_json(batch_errors)

        return batch_data_array

    def submit_callback(
        self,
        callback: Callable[..., Any],
        content: dict | None = None,
        halt_on_error: bool = True,
    ) -> bool:
        """Submit batch data to ThreatConnect and poll in a separate thread.

        The "normal" submit methods run in serial which will block when the batch poll is running.
        Using this method the submit is done in serial, but the poll method is run in a thread,
        which should allow the App to continue downloading and processing data while the batch
        poll process is running. Only one batch submission is allowed at a time so that any
        critical errors returned from batch can be handled before submitting a new batch job.

        Args:
            callback: The callback method that will handle
                the batch status when polling is complete.
            content: The dict of groups and indicator data (e.g., {"group": [], "indicator": []}).
            halt_on_error: If True the process should halt if any errors are encountered.

        Raises:
            RuntimeError: Raised on invalid callback method.

        Returns:
            bool: False when there is not data to process, else True
        """
        # user provided content or grab content from local group/indicator lists
        if content is not None:
            # process content
            pass
        else:
            content = self.data
        file_data = content.pop('file', {})

        # return False when end of data is reached
        if not content.get('group') and not content.get('indicator'):
            return False

        # block here is there is already a batch submission being processed
        if self._submit_thread and hasattr(self._submit_thread, 'is_alive'):
            self.log.info(
                'feature=batch, event=progress, status=blocked, '
                f'is-alive={self._submit_thread.is_alive()}'
            )
            self._submit_thread.join()
            self.log.debug(
                'feature=batch, event=progress, status=released, '
                f'is-alive={self._submit_thread.is_alive()}'
            )

        # submit the data and collect the response
        batch_data: dict = (
            self.submit_create_and_upload(content=content, halt_on_error=halt_on_error)
            .get('data', {})
            .get('batchStatus', {})
        )
        self.log.trace(f'feature=batch, event=submit-callback, batch-data={batch_data}')

        # launch batch polling in a thread
        self._submit_thread = self.submit_thread(
            name='submit-poll',
            target=self.submit_callback_thread,
            args=(batch_data, callback, file_data),
        )

        return True

    def submit_callback_thread(
        self,
        batch_data: dict,
        callback: Callable[..., Any],
        file_data: dict,
        halt_on_error: bool = True,
    ):
        """Submit data in a thread."""
        batch_id = batch_data.get('id')
        self.log.info(f'feature=batch, event=progress, batch-id={batch_id}')
        if batch_id:
            # when batch_id is None it indicates that batch submission was small enough to be
            # processed inline (without being queued)

            # poll for status
            batch_status = (
                self.poll(batch_id, halt_on_error=halt_on_error).get('data', {}).get('batchStatus')
            )

            # retrieve errors
            if batch_status is not None:
                error_count = batch_status.get('errorCount', 0)
                error_groups = batch_status.get('errorGroupCount', 0)
                error_indicators = batch_status.get('errorIndicatorCount', 0)
                if error_count > 0 or error_groups > 0 or error_indicators > 0:
                    batch_status['errors'] = self.errors(batch_id)
        else:
            batch_status = batch_data

        # launch file upload in a thread *after* batch status is returned. while only one batch
        # submission thread is allowed, there is no limit on file upload threads. the upload
        # status returned by file upload will be ignored when running in a thread.
        if file_data:
            self._file_threads.append(
                self.submit_thread(
                    name='submit-files',
                    target=self.submit_files,
                    args=(
                        file_data,
                        halt_on_error,
                    ),
                )
            )

        # send batch_status to callback
        if callable(callback):
            self.log.debug('feature=batch, event=calling-callback')
            try:
                callback(batch_status)
            except Exception as e:
                self.log.warning(f'feature=batch, event=callback-error, err="""{e}"""')

    def submit_create_and_upload(self, content: dict, halt_on_error: bool = True) -> dict:
        """Submit Batch request to ThreatConnect API.

        Args:
            content: The dict of groups and indicator data.
            halt_on_error: If True the process should halt if any errors are encountered.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        # special code for debugging App using batchV2.
        self.write_batch_json(content)

        # store the length of the batch data to use for poll interval calculations
        self.log.info(
            '''feature=batch, event=submit-create-and-upload, type=group, '''
            f'''count={len(content['group']):,}'''
        )
        self.log.info(
            '''feature=batch, event=submit-create-and-upload, type=indicator, '''
            f'''count={len(content['indicator']):,}'''
        )

        try:
            files = (('config', json.dumps(self.settings)), ('content', json.dumps(content)))
            params = {'includeAdditional': 'true'}
            r = self.session_tc.post('/v2/batch/createAndUpload', files=files, params=params)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                handle_error(
                    code=10510,
                    message_values=[r.status_code, r.text],
                    raise_error=halt_on_error,
                )
            return r.json()
        except Exception as e:
            handle_error(code=10505, message_values=[e], raise_error=halt_on_error)

        return {}

    def submit_files(self, file_data: dict, halt_on_error: bool = True) -> list[dict] | None:
        """Submit Files for Documents and Reports to ThreatConnect API.

        Critical Errors

        * There is insufficient document storage allocated to this account.

        Args:
            halt_on_error: If True any exception will raise an error.
            file_data: The file data to be submitted.

        Returns:
            dict: The upload status for each xid.
        """
        # check global setting for override
        if self.halt_on_file_error is not None:
            halt_on_error = self.halt_on_file_error

        upload_status = []
        self.log.info(f'feature=batch, action=submit-files, count={len(file_data)}')
        for xid, content_data in list(file_data.items()):
            del file_data[xid]  # win or loose remove the entry
            status = True

            # used for debug/testing to prevent upload of previously uploaded file
            if self.debug and xid in self.saved_xids:
                self.log.debug(
                    f'feature=batch-submit-files, action=skip-previously-saved-file, xid={xid}'
                )
                continue

            # process the file content
            content = content_data.get('fileContent')
            if callable(content):
                try:
                    content_callable_name = getattr(content, '__name__', repr(content))
                    self.log.trace(
                        f'feature=batch-submit-files, method={content_callable_name}, xid={xid}'
                    )
                    content = content_data.get('fileContent')(xid)
                except Exception as e:
                    self.log.warning(f'feature=batch, event=file-download-exception, err="""{e}"""')

            if content is None:
                upload_status.append({'uploaded': False, 'xid': xid})
                self.log.warning(f'feature=batch-submit-files, xid={xid}, event=content-null')
                continue

            api_branch = 'documents'
            if content_data.get('type') == 'Report':
                api_branch = 'reports'

            if self.debug and content_data.get('fileName'):
                # special code for debugging App using batchV2.
                fqfn = os.path.join(
                    self.debug_path_files,
                    f'''{api_branch}--{xid}--{content_data.get('fileName').replace('/', ':')}''',
                )
                if os.path.isdir(os.path.dirname(fqfn)):
                    with open(fqfn, 'wb') as fh:
                        if not isinstance(content, bytes):
                            content = content.encode()
                        fh.write(content)

            # Post File
            url = f'/v2/groups/{api_branch}/{xid}/upload'
            headers = {'Content-Type': 'application/octet-stream'}
            params = {'owner': self._owner, 'updateIfExists': 'true'}
            r = self.submit_file_content('POST', url, content, headers, params, halt_on_error)
            if r is None:
                return None

            if r.status_code == 401:
                # use PUT method if file already exists
                self.log.info('feature=batch, event=401-from-post, action=switch-to-put')
                r = self.submit_file_content('PUT', url, content, headers, params, halt_on_error)
                if r is None:
                    return None

            if not r.ok:
                status = False
                handle_error(
                    code=585,
                    message_values=[r.status_code, r.text],
                    raise_error=halt_on_error,
                )
            elif self.debug and self.enable_saved_file and xid not in self.saved_xids:
                # save xid "if" successfully uploaded and not already saved
                self.saved_xids = xid

            self.log.info(
                f'feature=batch, event=file-upload, status={r.status_code}, '
                f'xid={xid}, remaining={len(file_data)}'
            )
            upload_status.append({'uploaded': status, 'xid': xid})

        return upload_status

    def submit_file_content(
        self,
        method: str,
        url: str,
        data: bytes | str,
        headers: dict,
        params: dict,
        halt_on_error: bool = True,
    ) -> Response | None:
        """Submit File Content for Documents and Reports to ThreatConnect API.

        Args:
            method: The HTTP method for the request (POST, PUT).
            url: The URL for the request.
            data: The body (data) for the request.
            headers: The headers for the request.
            params: The query string parameters for the request.
            halt_on_error: If True any exception will raise an error.

        Returns:
            Response: The response from the request.
        """
        r = None
        try:
            r = self.session_tc.request(method, url, data=data, headers=headers, params=params)
        except Exception as e:
            handle_error(code=580, message_values=[e], raise_error=halt_on_error)
        return r

    def submit_job(self, halt_on_error: bool = True) -> int | None:
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
            r = self.session_tc.post('/v2/batch', json=self.settings)
        except Exception as e:
            handle_error(code=10505, message_values=[e], raise_error=halt_on_error)
            return None

        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            handle_error(
                code=10510,
                message_values=[r.status_code, r.text],
                raise_error=halt_on_error,
            )
        data = r.json()
        if data.get('status') != 'Success':
            handle_error(
                code=10510,
                message_values=[r.status_code, r.text],
                raise_error=halt_on_error,
            )
        self.log.debug(f'feature=batch, event=submit-job, status={data}')
        return data.get('data', {}).get('batchId')

    def submit_thread(
        self,
        name: str,
        target: Callable,
        args: tuple | None = None,
        kwargs: dict | None = None,
    ):
        """Start a submit thread.

        Args:
            name: The name of the thread.
            target: The method to call for the thread.
            args: The args to pass to the target method.
            kwargs: Additional args.
        """
        self.log.info(f'feature=batch, event=submit-thread, name={name}')
        args = args or ()
        t = None
        try:
            t = threading.Thread(name=name, target=target, args=args, kwargs=kwargs, daemon=True)
            t.start()
        except Exception:
            self.log.trace(traceback.format_exc())
        return t

    def write_error_json(self, errors: list):
        """Write the errors to a JSON file for debugging purposes.

        Args:
            errors: A list of errors to write out.
        """
        if self.debug:
            if not errors:
                errors = []
            # get timestamp as a string without decimal place and consistent length
            timestamp = str(int(time.time() * 10000000))
            error_json_file = os.path.join(self.debug_path_batch, f'errors-{timestamp}.json.gz')
            with gzip.open(error_json_file, mode='wt', encoding='utf-8') as fh:
                json.dump(errors, fh)

    def write_batch_json(self, content: dict):
        """Write batch json data to a file."""
        if self.debug and content:
            # get timestamp as a string without decimal place and consistent length
            timestamp = str(int(time.time() * 10000000))
            batch_json_file = os.path.join(self.debug_path_batch, f'batch-{timestamp}.json.gz')
            with gzip.open(batch_json_file, mode='wt', encoding='utf-8') as fh:
                json.dump(content, fh)

    @property
    def group_len(self) -> int:
        """Return the number of current groups."""
        return len(self.groups) + len(self.groups_shelf)

    @property
    def indicator_len(self) -> int:
        """Return the number of current indicators."""
        return len(self.indicators) + len(self.indicators_shelf)

    def __len__(self) -> int:
        """Return the number of groups and indicators."""
        return self.group_len + self.indicator_len

    def __str__(self) -> str:  # pragma: no cover
        """Return string representation of batch."""
        groups = []
        for group_data in self.groups.values():
            if isinstance(group_data, dict):
                groups.append(group_data)
            else:
                groups.append(group_data.data)
        for group_data in self.groups_shelf.values():
            if isinstance(group_data, dict):
                groups.append(group_data)
            else:
                groups.append(group_data.data)

        indicators = []
        for indicator_data in self.indicators.values():
            if isinstance(indicator_data, dict):
                indicators.append(indicator_data)
            else:
                indicators.append(indicator_data.data)
        for indicator_data in self.indicators_shelf.values():
            if isinstance(indicator_data, dict):
                indicators.append(indicator_data)
            else:
                indicators.append(indicator_data.data)

        data = {'group': groups, 'indicators': indicators}
        return json.dumps(data, indent=4, sort_keys=True)
