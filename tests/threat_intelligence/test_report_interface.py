# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# standard library
import os
from datetime import datetime, timedelta
from random import randint

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestReportGroups(TestThreatIntelligence):
    """Test TcEx Report Groups."""

    group_type = 'Report'
    owner = os.getenv('TC_OWNER')
    file_content = 'pytest report text'
    required_fields = {'file_name': 'pytest.pdf'}
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type, required_fields=self.required_fields)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_report_create(self):
        """Create a group using specific interface."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.report(**group_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get(ti.api_entity) == group_data.get(ti.api_entity)

        # cleanup group
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_report_add_attribute(self, request):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_report_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_report_add_tag(self, request):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_report_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_report_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_report_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_report_get_includes(self, request):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_report_get_attribute(self, request):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_report_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_report_get_tag(self, request):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_report_update(self, request):
        """Test updating group metadata."""
        super().group_update(request)

    #
    # Custom test cases
    #

    def tests_ti_report_file_content_update(self):
        """Test updating the file content of a Report."""
        helper_ti = self.ti_helper.create_group()

        # update file content (coverage)
        r = helper_ti.file_content(self.file_content)
        assert r.status_code == 200

    def tests_ti_report_file_content_no_update(self):
        """Test updating the file content of a Report that has not been created yet."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)

        # update file content (coverage)
        try:
            ti.file_content(self.file_content)
            assert False, 'failed to catch file content update on an report with no id.'
        except RuntimeError:
            assert True, 'caught file content update call on an report with no id'

    def tests_ti_report_file_name_update(self):
        """Test updating the file name of a Report."""
        helper_ti = self.ti_helper.create_group()

        # update file content (coverage)
        file_name = self.ti_helper.rand_filename()
        r = helper_ti.file_name(file_name)
        assert r.status_code == 200

    def tests_ti_report_file_name_no_update(self):
        """Test updating the file name of a Report that has not been created yet."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)

        # update file content (coverage)
        try:
            ti.file_name(self.ti_helper.rand_filename())
            assert False, 'failed to catch file name update on an report with no id.'
        except RuntimeError:
            assert True, 'caught file name update call on an report with no id'

    def tests_ti_report_file_size_update(self):
        """Create a label on a group."""
        helper_ti = self.ti_helper.create_group()

        # update file content (coverage)
        file_size = randint(1000, 10000)
        r = helper_ti.file_size(file_size)
        assert r.status_code == 200

    def tests_ti_report_file_size_no_update(self):
        """Create a label on a group."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)

        # update file content (coverage)
        try:
            file_size = randint(1000, 10000)
            ti.file_size(file_size)
            assert False, 'failed to catch file size update on an report with no id.'
        except RuntimeError:
            assert True, 'caught file size update call on an report with no id'

    def tests_ti_report_status_update(self):
        """Create a label on a group."""
        helper_ti = self.ti_helper.create_group()

        # update file content (coverage)
        r = helper_ti.status(self.ti_helper.rand_report_status())
        assert r.status_code == 200

    def tests_ti_report_status_no_update(self):
        """Create a label on a group."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)

        # update file content (coverage)
        try:
            ti.status(self.ti_helper.rand_report_status())
            assert False, 'failed to catch file status update on an report with no id.'
        except RuntimeError:
            assert True, 'caught file content status call on an report with no id'

    def tests_ti_report_file_published_date_update(self):
        """Create a label on a group."""
        helper_ti = self.ti_helper.create_group()

        # update file content (coverage)
        date = (datetime.now() - timedelta(days=2)).isoformat()
        r = helper_ti.publish_date(date)
        assert r.status_code == 200
        assert r.json().get('data').get(helper_ti.api_entity).get('publishDate')[:10] == date[:10]

    def tests_ti_report_file_published_date_no_update(self):
        """Create a label on a group."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)

        # update file content (coverage)
        try:
            ti.publish_date((datetime.now() - timedelta(days=2)).isoformat())
            assert False, 'failed to catch publish date update on an report with no id.'
        except RuntimeError:
            assert True, 'caught publish date update call on an report with no id'

    def tests_ti_report_download_update(self):
        """Create a label on a group."""
        helper_ti = self.ti_helper.create_group()

        # update file content (coverage)
        r = helper_ti.file_content(self.file_content)
        assert r.status_code == 200

        r = helper_ti.download()
        assert r.status_code == 200
        assert r.text == self.file_content

    def tests_ti_report_download_no_update(self):
        """Create a label on a group."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'owner': self.owner,
        }
        ti = self.ti.report(**group_data)

        # update file content (coverage)
        try:
            ti.download()
            assert False, 'failed to catch file download on an report with no id.'
        except RuntimeError:
            assert True, 'caught file download call on an report with no id'
