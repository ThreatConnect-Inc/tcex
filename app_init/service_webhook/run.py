# -*- coding: utf-8 -*-
"""Playbook App"""
# standard library
import traceback

# first-party
from app_lib import AppLib


# pylint: disable=no-member
def run(**kwargs):
    """Update path and run the App."""

    # update the path to ensure the App has access to required modules
    app_lib = AppLib()
    app_lib.update_path()

    # import modules after path has been updated

    # third-party
    from tcex import TcEx  # pylint: disable=import-outside-toplevel

    # first-party
    from app import App  # pylint: disable=import-outside-toplevel

    tcex = TcEx()

    try:
        # load App class
        app = App(tcex)

        # set app property in testing framework
        if callable(kwargs.get('set_app')):
            kwargs.get('set_app')(app)

        # configure custom trigger message handler
        tcex.service.create_config_callback = app.create_config_callback
        tcex.service.delete_config_callback = app.delete_config_callback
        tcex.service.shutdown_callback = app.shutdown_callback
        tcex.service.webhook_event_callback = app.webhook_event_callback

        # perform prep/setup operations
        app.setup(**{})

        # listen on channel/topic
        tcex.service.listen()

        # start heartbeat threads
        tcex.service.heartbeat()

        # inform TC that micro-service is Ready
        tcex.service.ready = True

        # loop until exit
        if hasattr(app, 'loop_forever'):
            app.loop_forever()  # pylint: disable=no-member
        else:
            tcex.log.info('Looping until shutdown')
            while tcex.service.loop_forever(sleep=1):
                pass

        # perform cleanup/teardown operations
        app.teardown(**{})

        # explicitly call the exit method
        tcex.playbook.exit(msg=app.exit_message)

    except Exception as e:
        main_err = f'Generic Error.  See logs for more details ({e}).'
        tcex.log.error(traceback.format_exc())
        tcex.playbook.exit(1, main_err)


if __name__ == '__main__':
    # Run the App
    run()
