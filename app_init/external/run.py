# -*- coding: utf-8 -*-
"""Job App"""
# standard library
import os
import traceback

# first-party
from app_lib import AppLib


def run():
    """Update path and run the App."""

    # update the path to ensure the App has access to required modules
    app_lib = AppLib()
    app_lib.update_path()

    # import modules after path has been updated
    # third-party
    from tcex import TcEx  # pylint: disable=import-outside-toplevel

    # first-party
    from app import App  # pylint: disable=import-outside-toplevel

    config_file = 'app_config.json'
    if not os.path.isfile(config_file):
        print(f'Missing {config_file} config file.')

    tcex = TcEx(config_file=config_file)

    try:
        # load App class
        app = App(tcex)

        # perform prep/setup operations
        app.setup()

        # run the App logic
        app.run()

        # perform cleanup/teardown operations
        app.teardown()

        # explicitly call the exit method
        tcex.exit(msg=app.exit_message)

    except Exception as e:
        main_err = f'Generic Error.  See logs for more details ({e}).'
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)


if __name__ == '__main__':
    # Run the App
    run()
