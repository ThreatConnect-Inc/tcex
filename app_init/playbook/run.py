# -*- coding: utf-8 -*-
"""Playbook App"""
import os
import sys
import traceback


def _update_app_path():
    """Update sys path to ensure all required modules can be found.

    All Apps must be able to access included modules, this method will ensure that the system path
    has been updated to include the "cwd" and "lib_" directories.  This is normally handled by
    the __main__.py file, but in some cases an App may be called directly.
    """

    cwd = os.getcwd()
    lib_dir = os.path.join(os.getcwd(), 'lib_')
    lib_latest = os.path.join(os.getcwd(), 'lib_latest')

    # insert the lib_latest directory into the system Path if no other lib directory found. This
    # entry will be bumped to index 1 after adding the current working directory.
    if not [p for p in sys.path if lib_dir in p]:
        sys.path.insert(0, lib_latest)

    # insert the current working directory into the system Path for the App, ensuring that it is
    # always the first entry in the list.
    try:
        sys.path.remove(cwd)
    except ValueError:
        pass
    sys.path.insert(0, cwd)


if __name__ == '__main__':

    # update the path to ensure the App has access to required modules
    _update_app_path()

    # import modules after path has been updated
    from tcex import TcEx
    from app import App

    tcex = TcEx()

    try:
        # load App class
        app = App(tcex)

        # perform prep/setup operations
        app.setup()

        # run the App logic
        if hasattr(app.args, 'tc_action') and app.args.tc_action is not None:
            # if the args NameSpace has the reserved arg of "tc_action", this arg value is used to
            # triggers a call to the app.<tc_action>() method.  an exact match to the method is
            # tried first, followed by a normalization of the tc_action value, and finally an
            # attempt is made to find the reserved "tc_action_map" property to map value to method.
            tc_action = app.args.tc_action
            tc_action_formatted = tc_action.lower().replace(' ', '_')
            tc_action_map = 'tc_action_map'  # reserved property name for action to method map
            # run action method
            if hasattr(app, tc_action):
                getattr(app, tc_action)()
            elif hasattr(app, tc_action_formatted):
                getattr(app, tc_action_formatted)()
            elif hasattr(app, tc_action_map):
                app.tc_action_map.get(app.args.tc_action)()  # pylint: disable=no-member
            else:
                tcex.exit(1, f'Action method ({app.args.tc_action}) was not found.')
        else:
            # default to run method
            app.run()

        # write requested value for downstream Apps
        tcex.playbook.write_output()
        app.write_output()  # pylint: disable=no-member

        # perform cleanup/teardown operations
        app.teardown()

        # explicitly call the exit method
        tcex.playbook.exit(msg=app.exit_message)

    except Exception as e:
        main_err = f'Generic Error.  See logs for more details ({e}).'
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)
