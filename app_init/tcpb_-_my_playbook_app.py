# -*- coding: utf-8 -*-
""" My Playbook App

This is NOT a functioning App.  It is intended to show common methods used when writing a playbook
App using the TcEx framework.
"""
import traceback

from tcex import TcEx

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

tcex = TcEx()

# App args
tcex.parser.add_argument('--my_input', required=True)
tcex.parser.add_argument('--my_choice', required=True)
tcex.parser.add_argument('--my_multi', action='append', required=True)
tcex.parser.add_argument('--my_boolean', action='store_true')
tcex.parser.add_argument('--my_hidden', action='store_true')
args = tcex.args


class MyApp(object):
    """String Operation App"""

    def __init__(self, _args):
        """Initialize class properties."""
        self.args = _args
        self.my_input = tcex.playbook.read(self.args.my_input)
        self.my_choice = tcex.playbook.read(self.args.my_choice)
        self.my_multi = tcex.playbook.read(self.args.my_multi, True)  # alway return list
        self.my_boolean = tcex.playbook.read(self.args.my_boolean)
        self.my_hidden = tcex.playbook.read(self.args.my_hidden)

        # init output
        self.my_output = []

    def do_the_thing(self):
        """Do something."""
        tcex.log.info('doing the thing')
        self.my_output.append(self.my_input)
        self.my_output.append(self.my_choice)
        self.my_output.extend(self.my_multi)
        self.my_output.append(str(self.my_boolean))
        self.my_output.append(self.my_hidden)

    def write_output(self):
        """Write the Playbook output variables."""
        tcex.log.info('writing output')
        tcex.playbook.create_output('mypbapp.output.0', self.my_output[0])
        tcex.playbook.create_output('mypbapp.output', self.my_output)


if __name__ == '__main__':
    try:
        app = MyApp(args)
        tcex.log.info('my_input: {}'.format(app.my_input))

        # do something
        app.do_the_thing()

        # write requested value for downstream Apps
        app.write_output()

        # write message and gracefully exit the App
        tcex.exit(0, 'Success.')

    except Exception as e:
        main_err = 'Generic Error.  See logs for more details ({}).'.format(e)
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)
