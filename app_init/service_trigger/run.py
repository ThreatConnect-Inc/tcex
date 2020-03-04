# -*- coding: utf-8 -*-
"""Playbook App"""
import traceback

from app_lib import AppLib


# pylint: disable=no-member
if __name__ == '__main__':

    # update the path to ensure the App has access to required modules
    app_lib = AppLib()
    app_lib.update_path()

    # import modules after path has been updated
    from tcex import TcEx
    from app import App

    tcex = TcEx()

    try:
        # load App class
        app = App(tcex)

        # configure custom trigger message handler
        tcex.service.create_config_callback = app.create_config_callback
        tcex.service.delete_config_callback = app.delete_config_callback
        tcex.service.shutdown_callback = app.shutdown_callback

        # perform prep/setup operations
        app.setup()

        # listen on channel/topic
        tcex.service.listen()

        # start heartbeat threads
        tcex.service.heartbeat()

        # inform TC that micro-service is Ready
        tcex.service.ready = True

        # run app logic
        app.run()

        # perform cleanup/teardown operations
        app.teardown()

        # explicitly call the exit method
        tcex.playbook.exit(msg=app.exit_message)

    except Exception as e:
        main_err = f'Generic Error.  See logs for more details ({e}).'
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)
