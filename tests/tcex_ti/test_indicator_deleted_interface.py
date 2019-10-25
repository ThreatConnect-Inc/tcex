# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import datetime
import random

from ..tcex_init import tcex


# pylint: disable=W0201
class TestIndicatorDeletedInterface:
    """Test TcEx deleted endpoint for indicator types."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    """
        Test Address branch
    """
    def test_address_deleted(self, ip='14.111.14.15'):
        deleted_since = tcex.utils.format_datetime(
            '1 hour ago', 'UTC', '%Y-%m-%dT%H:%M:%SZ'
        )
        self.address_delete(ip)

        indicator_ti = self.ti.indicator(indicator_type='Address')
        found_indicator = False
        for i in indicator_ti.deleted(deleted_since=deleted_since):
            if i.get('summary') == ip:
                found_indicator = True

        assert found_indicator

    def address_create(self, ip):
        """Test address create."""
        ti = self.ti.indicator(indicator_type='Address', owner=tcex.args.tc_owner, ip=ip)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('address').get('ip') == ip

    def address_delete(self, ip):
        """Test address delete."""
        # create indicator
        self.address_create(ip)

        # delete indicator
        ti = self.ti.indicator(indicator_type='Address', owner=tcex.args.tc_owner, ip=ip)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    """
        Test CIDR Branch
    """
    def test_cidr_deleted(self, block='1.1.1.7/8'):
        deleted_since = tcex.utils.format_datetime(
            '1 hour ago', 'UTC', '%Y-%m-%dT%H:%M:%SZ'
        )
        self.cidr_delete(block)

        indicator_ti = self.ti.indicator(indicator_type='CIDR')
        found_indicator = False
        for i in indicator_ti.deleted(deleted_since=deleted_since):
            if i.get('summary') == block:
                found_indicator = True

        assert found_indicator

    def cidr_create(self, block):
        """Test cidr create."""
        ti = self.ti.indicator(indicator_type='CIDR', owner=tcex.args.tc_owner, block=block)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('Block') == block

    def cidr_delete(self, block):
        """Test cidr delete."""
        # create indicator
        self.cidr_create(block)

        # delete indicator
        ti = self.ti.indicator(indicator_type='CIDR', owner=tcex.args.tc_owner, block=block)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    """
        Test Email Address Branch
    """
    def test_email_address_deleted(self, indicator='foo@badwebsite.com'):
        deleted_since = tcex.utils.format_datetime(
            '1 hour ago', 'UTC', '%Y-%m-%dT%H:%M:%SZ'
        )
        self.email_address_delete(indicator)

        indicator_ti = self.ti.indicator(indicator_type='EMAILADDRESS')
        found_indicator = False
        for i in indicator_ti.deleted(deleted_since=deleted_since):
            if i.get('summary') == indicator:
                found_indicator = True

        assert found_indicator

    def email_address_create(self, address):
        """Test email_address create."""
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('emailAddress').get('address') == address

    def email_address_delete(self, address):
        """Test email_address delete."""
        # create indicator
        self.email_address_create(address)

        # delete indicator
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    """
        Test File Branch
    """
    def test_file_deleted(self, indicator='1d59bb787ae38a1dda90cf82d09e3648'):
        deleted_since = tcex.utils.format_datetime(
            '1 hour ago', 'UTC', '%Y-%m-%dT%H:%M:%SZ'
        )
        self.file_delete(indicator)

        indicator_ti = self.ti.indicator(indicator_type='File')
        found_indicator = False
        for i in indicator_ti.deleted(deleted_since=deleted_since):
            if i.get('summary') == indicator.upper():
                found_indicator = True

        assert found_indicator

    def file_create(self, md5):
        """Test file create."""
        random_size = random.randint(1, 101)
        ti = self.ti.file(
            owner=tcex.args.tc_owner, md5=md5, size=random_size
        )
        r = ti.create()
        assert r.status_code == 201
        ti_data = r.json()
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('md5', None) == md5.upper()
        assert ti_data.get('data').get('file').get('size', None) == random_size

    def file_delete(self, md5):
        """Test email_address delete."""
        # create indicator
        self.file_create(md5)

        # delete indicator
        ti = self.ti.file(md5=md5, owner=tcex.args.tc_owner)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    """
        Test Host Branch
    """
    def test_host_deleted(self, indicator='www.go0gle.co.uk'):
        deleted_since = tcex.utils.format_datetime(
            '1 hour ago', 'UTC', '%Y-%m-%dT%H:%M:%SZ'
        )
        self.host_delete(indicator)

        indicator_ti = self.ti.indicator(indicator_type='Host')
        found_indicator = False
        for i in indicator_ti.deleted(deleted_since=deleted_since):
            if i.get('summary') == indicator:
                found_indicator = True

        assert found_indicator

    def host_create(self, host):
        """Test file create."""
        ti = self.ti.host(
            owner=tcex.args.tc_owner, hostname=host
        )
        r = ti.create()
        assert r.status_code == 201
        ti_data = r.json()
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('host').get('hostName', None) == host

    def host_delete(self, host):
        """Test email_address delete."""
        # create indicator
        self.host_create(host)

        # delete indicator
        ti = self.ti.host(hostname=host, owner=tcex.args.tc_owner)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    """
         Test URL Branch
     """
    def test_url_deleted(self, indicator='https://www.go0gle.co.uk/virus'):
        deleted_since = tcex.utils.format_datetime(
            '1 hour ago', 'UTC', '%Y-%m-%dT%H:%M:%SZ'
        )
        self.url_delete(indicator)

        indicator_ti = self.ti.indicator(indicator_type='URL')
        found_indicator = False
        for i in indicator_ti.deleted(deleted_since=deleted_since):
            if i.get('summary') == indicator:
                found_indicator = True

        assert found_indicator

    def url_create(self, url):
        """Test file create."""
        ti = self.ti.url(
            owner=tcex.args.tc_owner, url=url
        )
        r = ti.create()
        assert r.status_code == 201
        ti_data = r.json()
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('url', {}).get('text') == url

    def url_delete(self, url):
        """Test email_address delete."""
        # create indicator
        self.url_create(url)

        # delete indicator
        ti = self.ti.url(url=url, owner=tcex.args.tc_owner)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'