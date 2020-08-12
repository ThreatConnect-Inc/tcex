#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework LayoutJson."""
# standard library
import json
import logging
import os
from collections import OrderedDict


class AppFeatureAdvanceRequest:
    """AdvancedRequest Module"""

    def __init__(self, lj, json_data, prefix):
        """Initialize Class properties."""
        self.lj = lj
        self.json_data = json_data
        self._prefix = prefix

    @staticmethod
    def get_index(params, key, value):
        """Return the index of a dict from a list of dicts."""
        for index, data in enumerate(params):
            if data.get(key) == value:
                return index
        return None

    @property
    def inputs(self):
        """Return Advanced Request Inputs."""
        return [
            {'display': 'tc_action in (\'Advanced Request\')', 'name': 'tc_adv_req_path'},
            {'display': 'tc_action in (\'Advanced Request\')', 'name': 'tc_adv_req_http_method'},
            {'display': 'tc_action in (\'Advanced Request\')', 'name': 'tc_adv_req_params'},
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': 'tc_adv_req_exclude_null_params',
            },
            {'display': 'tc_action in (\'Advanced Request\')', 'name': 'tc_adv_req_headers'},
            {
                'display': (
                    'tc_action in (\'Advanced Request\') AND tc_adv_req_http_method in '
                    '(\'POST\', \'PUT\', \'DELETE\', \'PATCH\')'
                ),
                'name': 'tc_adv_req_body',
            },
            {
                'display': (
                    'tc_action in (\'Advanced Request\') AND tc_adv_req_http_method in '
                    '(\'POST\', \'PUT\', \'DELETE\', \'PATCH\')'
                ),
                'name': 'tc_adv_req_urlencode_body',
            },
            {'display': 'tc_action in (\'Advanced Request\')', 'name': 'tc_adv_req_fail_on_error'},
        ]

    @property
    def outputs(self):
        """Return Advanced Request Outputs."""
        return [
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': f'{self.prefix}.request.content',
            },
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': f'{self.prefix}.request.content.binary',
            },
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': f'{self.prefix}.request.headers',
            },
            {'display': 'tc_action in (\'Advanced Request\')', 'name': f'{self.prefix}.request.ok'},
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': f'{self.prefix}.request.reason',
            },
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': f'{self.prefix}.request.status_code',
            },
            {
                'display': 'tc_action in (\'Advanced Request\')',
                'name': f'{self.prefix}.request.url',
            },
        ]

    @property
    def prefix(self):
        """Return prefix for output variables."""
        if self._prefix is None:
            self._prefix = 'unknown'
            for o in self.lj.outputs:
                self._prefix = o.get('name').split('.')[0]
        return self._prefix

    def update(self):
        """Update the install.json inputs and outputs."""
        self.update_inputs()
        self.update_inputs_display()
        self.update_outputs()
        self.update_outputs_display()

    def update_inputs(self):
        """Update install.json param inputs."""
        for i in self.inputs:
            configure_index = self.get_index(self.json_data.get('inputs'), 'title', 'Configure')

            if i.get('name') in [
                p.get('name') for p in self.json_data['inputs'][configure_index]['parameters']
            ]:
                # replace existing data
                index = self.get_index(
                    self.json_data['inputs'][configure_index]['parameters'], 'name', i.get('name')
                )
                self.json_data['inputs'][configure_index]['parameters'][index] = i
            else:
                # append input
                self.json_data['inputs'][configure_index]['parameters'].append(i)

    def update_inputs_display(self):
        """Update any inputs that do not have a display value."""
        for i in self.json_data.get('inputs'):
            if i.get('title') in ['Action', 'Connection']:
                # only update display for inputs in Configure and Advanced sections
                continue
            for p in i.get('parameters'):
                if p.get('display') is None:
                    p['display'] = '''tc_action not in ('Advanced Request')'''

    def update_outputs(self):
        """Update install.json param inputs."""
        for o in self.outputs:
            # check to see if output was previously added
            if o.get('name') in [o.get('name') for o in self.json_data.get('outputs', [])]:
                # replace existing data
                index = self.get_index(self.json_data['outputs'], 'name', o.get('name'))
                self.json_data['outputs'][index] = o
            else:
                # append input
                self.json_data['outputs'].append(o)

    def update_outputs_display(self):
        """Update any outputs that do not have a display value."""
        for o in self.json_data.get('outputs'):
            if o.get('display') is None:
                o['display'] = '''tc_action not in ('Advanced Request')'''


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
            with open(self.filename, 'r') as fh:
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

    def update(self, features=None, prefix=None):
        """Update the layouts.json file."""
        # features from the instal.json
        features = features or []

        # get fresh copy of layout.json contents
        layout_data = self.contents

        # APP-86 - sort output data by name
        self.update_sort_outputs(layout_data)

        # update contents
        self._contents = layout_data

        # app feature - update layout_json.json for Advanced Request
        if 'advancedRequest' in features and prefix is not None:
            afar = AppFeatureAdvanceRequest(self, layout_data, prefix)
            afar.update()

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
