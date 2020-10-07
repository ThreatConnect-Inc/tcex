#!/usr/bin/env python
"""TcEx Framework LayoutJson."""
# standard library
import json
import logging
import os
from collections import OrderedDict


class LayoutJson:
    """Object for layout.json file.

    Args:
        filename (str, optional): The config filename. Defaults to layout.json.
        path (str, optional): The path to the file. Defaults to os.getcwd().
        logger (logging.Logger, optional): A instance of Logger. Defaults to None.
    """

    def __init__(self, filename=None, path=None, logger=None):
        """Initialize class properties."""
        self._filename = filename or 'layout.json'
        self._path = path or os.getcwd()
        self.log = logger or logging.getLogger('layout_json')

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
            with open(self.filename) as fh:
                self._contents = json.load(fh, object_pairs_hook=OrderedDict)
        return self._contents

    def create(self, inputs, outputs):
        """Create new layout.json file based on inputs and outputs."""
        lj = OrderedDict()

        # add inputs
        lj['inputs'] = []
        step = OrderedDict()
        step['parameters'] = []
        step['sequence'] = 1
        step['title'] = 'Action'
        lj['inputs'].append(step)
        step = OrderedDict()
        step['parameters'] = []
        step['sequence'] = 2
        step['title'] = 'Connection'
        lj['inputs'].append(step)
        step = OrderedDict()
        step['parameters'] = []
        step['sequence'] = 3
        step['title'] = 'Configure'
        lj['inputs'].append(step)
        step = OrderedDict()
        step['parameters'] = []
        step['sequence'] = 4
        step['title'] = 'Advanced'
        lj['inputs'].append(step)

        # add outputs
        lj['outputs'] = []

        for i in sorted(inputs):
            if i.get('name') == 'tc_action':
                lj['inputs'][0]['parameters'].append({'name': 'tc_action'})
            elif i.get('hidden') is True:
                lj['inputs'][2]['parameters'].append(
                    {'display': "'hidden' != 'hidden'", 'hidden': 'true', 'name': i.get('name')}
                )
            else:
                lj['inputs'][2]['parameters'].append({'display': '', 'name': i.get('name')})

        for o in sorted(outputs):
            lj['outputs'].append({'display': '', 'name': o.get('name')})

        # write layout file to disk
        self.write(lj)

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

    def update(self, features=None):
        """Update the layouts.json file."""
        # features from the instal.json
        features = features or []

        # get fresh copy of layout.json contents
        layout_data = self.contents

        # APP-86 - sort output data by name
        self.update_sort_outputs(layout_data)

        # update contents
        self._contents = layout_data

        # write updated content
        self.write(layout_data)

    @staticmethod
    def update_sort_outputs(layout_data):
        """Sort output field by name."""
        # APP-86 - sort output data by name
        layout_data['outputs'] = sorted(layout_data.get('outputs', []), key=lambda i: i['name'])

    def write(self, json_data):
        """Write updated profile file.

        Args:
            json_data (dict): The profile data.
        """
        with open(self.filename, 'w') as fh:
            json.dump(json_data, fh, indent=2, sort_keys=False)
            fh.write('\n')

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
