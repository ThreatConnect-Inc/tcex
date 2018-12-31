# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import json
import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413

TEST_DATASTORE_PATH = 'testing'


def test_creation():
    """Test Datastore creation"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    body = {'one': 1}
    results = resource.create('organization', TEST_DATASTORE_PATH, 1, json.dumps(body)).get('data')
    assert results
    assert results['_shards']['successful'] == 1
    assert results['_type'] == TEST_DATASTORE_PATH


def test_retrieval():
    """Test Datastore retrieval"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    results = resource.read('organization', TEST_DATASTORE_PATH, 1).get('data')
    assert results
    assert results['_source'] == {'one': 1}
    assert results['found']
    assert results['_type'] == TEST_DATASTORE_PATH


def test_creation_with_string_path():
    """Test Datastore creation with strint path"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    body = {'two': 2}
    results = resource.create('organization', TEST_DATASTORE_PATH, 'testing', json.dumps(body)).get(
        'data'
    )
    assert results
    assert results['_shards']['successful'] == 1
    assert results['_type'] == TEST_DATASTORE_PATH


def test_retrieval_with_string_path():
    """Test Datastore retrieval with strint path"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    results = resource.read('organization', TEST_DATASTORE_PATH, 'testing').get('data')
    assert results
    assert results['_source'] == {'two': 2}
    assert results['found']
    assert results['_type'] == TEST_DATASTORE_PATH


def test_creation_path_with_spaces():
    """Test Datastore creation with space in the path"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    body = {'three': 3}
    results = resource.create(
        'organization', TEST_DATASTORE_PATH, 'test ing', json.dumps(body)
    ).get('data')
    assert results
    assert results['_shards']['successful'] == 1
    assert results['_type'] == TEST_DATASTORE_PATH


def test_retrieval_path_with_spaces():
    """Try retrieving an entry in the datastore where the path has a space in it."""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    results = resource.read('organization', TEST_DATASTORE_PATH, 'test ing').get('data')
    assert results
    assert results['_source'] == {'three': 3}
    assert results['found']
    assert results['_type'] == TEST_DATASTORE_PATH


def test_creation_path_with_unicode():
    """Test Datastore creation with unicode path"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    body = {'four': 4}
    results = resource.create('organization', TEST_DATASTORE_PATH, 'niño', json.dumps(body)).get(
        'data'
    )
    assert results
    assert results['_shards']['successful'] == 1
    assert results['_type'] == TEST_DATASTORE_PATH


def test_retrieval_path_with_unicode():
    """Test Datastore retrieval with unicode path"""
    tcex = utility.init_tcex(requires_tc_token=True)
    resource = tcex.resources.DataStore(tcex)
    results = resource.read('organization', TEST_DATASTORE_PATH, 'niño').get('data')
    assert results
    assert results['_source'] == {'four': 4}
    assert results['found']
    assert results['_type'] == TEST_DATASTORE_PATH


@pytest.fixture(scope='session', autouse=True)
def cleanup(request):
    """Cleanup the datastore."""

    def clear_datastore():
        tcex = utility.init_tcex(requires_tc_token=True)
        resource = tcex.resources.DataStore(tcex)
        results = resource.delete('organization', TEST_DATASTORE_PATH, 1).get('data')
        assert results['_shards']['successful'] == 1
        assert results['result'] == 'deleted'
        results = resource.delete('organization', TEST_DATASTORE_PATH, 'testing').get('data')
        assert results['_shards']['successful'] == 1
        assert results['result'] == 'deleted'
        results = resource.delete('organization', TEST_DATASTORE_PATH, 'test ing').get('data')
        assert results['_shards']['successful'] == 1
        assert results['result'] == 'deleted'
        results = resource.delete('organization', TEST_DATASTORE_PATH, 'niño').get('data')
        assert results['_shards']['successful'] == 1
        assert results['result'] == 'deleted'

    request.addfinalizer(clear_datastore)
