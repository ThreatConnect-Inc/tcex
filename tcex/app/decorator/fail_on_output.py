"""TcEx Framework Module"""

# standard library
from collections.abc import Callable
from typing import Any, cast

# third-party
import wrapt

# first-party
from tcex.exit import ExitCode
from tcex.tcex import TcEx


class FailOnOutput:
    """Fail App if return value (output) value conditions are met.

    This decorator allows for the App to exit on conditions defined in the function
    parameters.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @FailOnOutput(
            fail_on=['false'], fail_msg='Operation returned a value of "false".'
        )
        def my_method(data):
            return data.lowercase()

    Args:
        fail_enabled: Accepts a boolean or string value.  If a boolean value
            is provided that value will control enabling/disabling this feature. A string
            value should reference an item in the args namespace which resolves to a boolean.
            The value of this boolean will control enabling/disabling this feature.
        fail_msg: The message to log when raising RuntimeError.
        fail_msg_property: The App property containing the dynamic exit message.
        fail_on: Fail if return value from App method is in the list.
        write_output: Defaults to True. If true, will call App.write_outputs() before failing
            on matched fail_on value.
    """

    def __init__(
        self,
        fail_enabled: bool | str = True,
        fail_msg: str = 'Method returned invalid output.',
        fail_on: list | None = None,
        fail_msg_property: str | None = None,
        write_output: bool = True,
    ):
        """Initialize instance properties."""
        self.fail_enabled = fail_enabled
        self.fail_msg = fail_msg
        self.fail_on = fail_on or []
        self.fail_msg_property = fail_msg_property
        self.write_output = write_output

    @wrapt.decorator
    def __call__(self, *wrapped_args) -> Any:
        """Implement __call__ function for decorator.

        Args:
            wrapped: The wrapped function which in turns
                needs to be called by your wrapper function.
            instance: The object to which the wrapped
                function was bound when it was called.
            args: The list of positional arguments supplied
                when the decorated function was called.
            kwargs: The dictionary of keyword arguments
                supplied when the decorated function was called.

        Returns:
            function: The custom decorator function.
        """
        # using wrapped args to support typing hints in PyRight
        wrapped: Callable = wrapped_args[0]
        app: Any = wrapped_args[1]
        args: list = wrapped_args[2] if len(wrapped_args) > 1 else []
        kwargs: dict = wrapped_args[3] if len(wrapped_args) > 2 else {}

        def fail() -> Any:
            """Call the function and store or append return value."""
            tcex = cast(TcEx, app.tcex)

            # call method to get output
            data = wrapped(*args, **kwargs)

            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            enabled = self.fail_enabled
            if isinstance(enabled, str):
                # get enabled value from App inputs
                enabled = getattr(tcex.inputs.model, enabled)
                if not isinstance(enabled, bool):  # pragma: no cover
                    raise RuntimeError(
                        'The fail_enabled value must be a boolean or resolved to bool.'
                    )
                tcex.log.debug(f'Fail enabled is {enabled} ({self.fail_enabled}).')

            failed = False
            if enabled:
                if isinstance(data, list):
                    # validate each value in the list of results.
                    for d in data:
                        if d in self.fail_on:
                            failed = True
                            break
                else:
                    if data in self.fail_on:
                        failed = True

                if failed:
                    if self.write_output:
                        tcex.app.playbook.output.process()
                        if hasattr(app, 'write_output'):
                            app.write_output()
                    app.exit_message = self.get_fail_msg(app)  # for test cases
                    tcex.exit.exit(ExitCode.FAILURE, self.get_fail_msg(app))
            return data

        return fail()

    def get_fail_msg(self, app) -> str:
        """Return the appropriate fail message."""
        fail_msg = self.fail_msg
        if isinstance(self.fail_msg_property, str):
            if self.fail_msg_property and hasattr(app, self.fail_msg_property):
                fail_msg = getattr(app, self.fail_msg_property)
        return fail_msg
