#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework LayoutJson."""
import json
import os
from collections import OrderedDict


class LayoutJson:
    """Object for layout.json file."""

    def __init__(self, filename=None, path=None):
        """Initialize class properties."""
        self._filename = filename or 'layout.json'
        self._path = path or os.getcwd()

        # properties
        self._contents = None

    @staticmethod
    def _to_bool(value):
        """Convert string value to bool."""
        bool_value = False
        if str(value).lower() in ['1', 'true']:
            bool_value = True
        return bool_value

    @property
    def contents(self):
        """Return layout.json contents."""
        if self._contents is None and self.has_layout:
            with open(self.filename, 'r') as fh:
                self._contents = json.load(fh, object_pairs_hook=OrderedDict)
        return self._contents

    def create(self, inputs, outputs):
        """Create new layout.json file based on inputs and outputs."""

        lj = {
            'inputs': [
                {'parameters': [], 'sequence': 1, 'title': 'Action'},
                {'parameters': [], 'sequence': 2, 'title': 'Connection'},
                {'parameters': [], 'sequence': 3, 'title': 'Configure'},
                {'parameters': [], 'sequence': 4, 'title': 'Advanced'},
            ],
            'outputs': [],
        }

        for i in inputs:
            if i.get('name') == 'tc_action':
                lj['inputs'][0]['parameters'].append({'name': 'tc_action'})
            elif i.get('hidden') is True:
                lj['inputs'][2]['parameters'].append(
                    {'display': "'hidden' != 'hidden'", 'hidden': 'true', 'name': i.get('name')}
                )
            else:
                lj['inputs'][2]['parameters'].append({'display': '', 'name': i.get('name')})

        for o in outputs:
            lj['outputs'].append({'display': '', 'name': o.get('name')})

        with open(self.filename, 'w') as fh:
            fh.write(f'{json.dumps(lj, indent=2, sort_keys=False)}\n')

    @property
    def filename(self):
        """Return the fqpn for the layout.json file."""
        return os.path.join(self._path, self._filename)

    @property
    def has_layout(self):
        """Return True if App has layout.json file."""
        if os.path.isfile(self.filename):
            return True
        return False

    @property
    def params_dict(self):
        """Return layout.json params in a flattened dict with name param as key."""
        parameters = {}
        for i in self.inputs:
            for p in i.get('parameters', []):
                parameters.setdefault(p.get('name'), p)
        return parameters

    @property
    def parameters_names(self):
        """Return layout.json params in a flattened dict with name param as key."""
        return self.params_dict.keys()

    @property
    def outputs_dict(self):
        """Return layout.json outputs in a flattened dict with name param as key."""
        outputs = {}
        for o in self.outputs:
            outputs.setdefault(o.get('name'), o)
        return outputs

    #
    # properties
    #

    @property
    def inputs(self):
        """Return property."""
        return self.contents.get('inputs', [])

    @property
    def outputs(self):
        """Return property."""
        return self.contents.get('outputs', [])
