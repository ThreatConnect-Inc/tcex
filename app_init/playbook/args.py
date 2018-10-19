# -*- coding: utf-8 -*-
""" Auto-generated Playbook Args """

class Args(object):
    """ Playbook Args """

    def __init__(self, _tcex):
        """ Initialize class properties. """
        _tcex.parser.add_argument('--indent', default=4)
        _tcex.parser.add_argument('--json_data', required=True)
        _tcex.parser.add_argument('--sort_keys', action='store_true')
