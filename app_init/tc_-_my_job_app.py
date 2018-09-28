# -*- coding: utf-8 -*-
""" My Job App

This is NOT a functioning App.  It is intended to show common methods used when writing a Job
App using the TcEx framework.
"""
import time
import traceback

from tcex import TcEx

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

tcex = TcEx()

# App args
tcex.parser.add_argument('--username', required=True)
tcex.parser.add_argument('--password', required=True)
tcex.parser.add_argument('--my_choice', required=True)
tcex.parser.add_argument('--my_multi', action='append', required=True)
tcex.parser.add_argument('--my_boolean', action='store_true')
tcex.parser.add_argument('--last_run', default='7 days ago')
tcex.parser.add_argument('--my_hidden', action='store_true')
args = tcex.args


class MyApp(object):
    """String Operation App"""

    def __init__(self, _args):
        """Initialize class properties."""
        self.args = _args

        # init output
        self.my_output = []

    def do_the_thing(self):
        """Do something."""
        tcex.log.info('doing the thing')
        self.my_output.append(self.args.username)
        self.my_output.append(self.args.password)
        self.my_output.append(self.args.my_choice)
        self.my_output.extend(self.args.my_multi)
        self.my_output.append(str(self.args.my_boolean))
        self.my_output.append(self.args.my_hidden)


if __name__ == '__main__':
    try:
        # get app init timestamp for last_run
        last_run = time.time()

        # get MyApp instance
        app = MyApp(args)
        tcex.log.info('username: {}'.format(args.username))

        # do something
        app.do_the_thing()

        # store persistent value
        tcex.results_tc('last_run', last_run)

        # write message and gracefully exit the App
        tcex.exit(0, 'Success.')

    except Exception as e:
        tcex.results_tc('last_run', args.last_run)
        main_err = 'Generic Error.  See logs for more details ({}).'.format(e)
        tcex.log.error(traceback.format_exc())
        tcex.exit(1, main_err)
