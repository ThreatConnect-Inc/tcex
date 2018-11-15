#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from batch_group_tests import batch_group_creation_interface_1
import validator
import utility


def test_document_download():
    """Test downloading a document from TC."""
    tcex_instance = utility.init_tcex()
    owner = tcex_instance.args.api_default_org

    # create a document
    batch = tcex_instance.batch(owner)
    batch_group_creation_interface_1.document_create(batch)
    batch.submit_all()

    # get the group
    groups = validator.get_groups(tcex_instance)
    document_id = groups[0]['id']

    # try to download the document
    doc = tcex_instance.resources.Document(tcex_instance)
    doc.owner = owner
    doc.download(document_id)

    document_contents = ''
    for results in doc:  # pagination
        document_contents = results['data']
    assert document_contents == 'Example file content'
