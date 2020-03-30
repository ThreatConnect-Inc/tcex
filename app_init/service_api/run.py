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
    from tcex import TcEx  # pylint: disable=import-outside-toplevel
    from app import App  # pylint: disable=import-outside-toplevel

    tcex = TcEx()

    try:
        # load App class
        app = App(tcex)

        # perform prep/setup operations
        app.setup()

        # configure custom trigger message handler
        tcex.service.api_event_callback = app.api_event_callback

        # listen on channel/topic
        tcex.service.listen()

        # start heartbeat threads
        tcex.service.heartbeat()

        # inform TC that micro-service is Ready
        tcex.service.ready = True

        # loop until exit
        tcex.service.loop_forever()

        # start the webhook trigger (blocking)
        # tcex.service.api_service(callback=app.api_callback)

        # perform cleanup/teardown operations
        app.teardown()

        # explicitly call the exit method
        tcex.playbook.exit(msg=app.exit_message)

    except Exception as e:
        main_err = f'Generic Error.  See logs for more details ({e}).'
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)
