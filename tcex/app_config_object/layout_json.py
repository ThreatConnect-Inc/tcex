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
        self.filename = filename or 'layout.json'
        if path is not None:
            self.filename = os.path.join(path, self.filename)

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
        if self._contents is None:
            with open(self.filename, 'r') as fh:
                self._contents = json.load(fh, object_pairs_hook=OrderedDict)
        return self._contents

    @property
    def parameters_dict(self):
        """Return layout.json params in a flattened dict with name param as key."""
        parameters = {}
        for i in self.inputs:
            for p in i.get('parameters', []):
                parameters.setdefault(p.get('name'), p)
        return parameters

    @property
    def parameters_names(self):
        """Return layout.json params in a flattened dict with name param as key."""
        return self.parameters_dict.keys()

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
