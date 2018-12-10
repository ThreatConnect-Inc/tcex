# -*- coding: utf-8 -*-
"""Playbook App"""
import traceback
import sys

from tcex import TcEx

from app import App


# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=E1101
    get_input = raw_input  # noqa: F821; pylint: disable=E0602

tcex = TcEx()

if __name__ == '__main__':
    try:
        # load App class
        app = App(tcex)

        # parse args
        app.parse_args()

        # perform prep/startup operations
        app.start()

        # run the App logic
        if hasattr(app.args, 'tc_action') and app.args.tc_action is not None:
            # if the args NameSpace has the reserved arg of "tc_action", this arg value is used to
            # triggers a call to the app.<tc_action>() method.  an exact match to the method is
            # tried first, followed by a normalization of the tc_action value, and finally an
            # attempt is made to find the reserved "tc_action_map" property to map value to method.
            tc_action = app.args.tc_action
            tc_action_formatted = tc_action.lower().replace(' ', '_')
            tc_action_map = 'tc_action_map'  # reserved property name for action to method map
            try:
                # run action method
                if hasattr(app, tc_action):
                    getattr(app, tc_action)()
                elif hasattr(app, tc_action_formatted):
                    getattr(app, tc_action_formatted)()
                elif hasattr(app, tc_action_map):
                    app.tc_action_map.get(app.args.tc_action)()
            except AttributeError:
                tcex.exit(1, 'Action method ({}) was not found.'.format(app.args.tc_action))
        else:
            # default to run method
            app.run()

        # write requested value for downstream Apps
        tcex.playbook.write_output()
        app.write_output()

        # perform cleanup operations
        app.done()

        # explicitly call the exit method
        tcex.playbook.exit(msg=app.exit_message)

    except Exception as e:
        main_err = 'Generic Error.  See logs for more details ({}).'.format(e)
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)
