# -*- coding: utf-8 -*-
"""Job App"""
import os
import sys
import traceback

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=E1101


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

    tcex = TcEx(config_file='app_config.json')

    try:
        # load App class
        app = App(tcex)

        # perform prep/startup operations
        app.start()

        # run the App logic
        app.run()

        # perform cleanup operations
        app.done()

        # explicitly call the exit method
        tcex.exit(msg=app.exit_message)

    except Exception as e:
        main_err = 'Generic Error.  See logs for more details ({}).'.format(e)
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)
