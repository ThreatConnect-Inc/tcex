"""TcEx Framework Module"""

import datetime as dt
import logging
from types import FunctionType
from typing import TYPE_CHECKING, Any, cast

import wrapt

from tcex.logger.trace_logger import TraceLogger

if TYPE_CHECKING:
    from collections.abc import Callable

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class Benchmark:
    """Log benchmarking times.

    This decorator will log the time of execution (benchmark_time) to the app.log file. It can be
    helpful in troubleshooting performance issues with Apps.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        import time


        @Benchmark()
        def my_method():
            time.sleep(1)
    """

    def __init__(
        self,
        microseconds: int = 0,
        milliseconds: int = 0,
        seconds: int = 0,
    ):
        """Initialize instance properties."""
        self.microseconds = microseconds
        self.milliseconds = milliseconds
        self.seconds = seconds

    @wrapt.decorator
    def __call__(self, *wrapped_args) -> Any:  # noqa: D417
        """Implement __call__ function for decorator.

        Args:
            wrapped (callable): The wrapped function which in turns
                needs to be called by your wrapper function.
            instance (App): The object to which the wrapped
                function was bound when it was called.
            args (list): The list of positional arguments supplied
                when the decorated function was called.
            kwargs (dict): The dictionary of keyword arguments
                supplied when the decorated function was called.

        Returns:
            function: The custom decorator function.
        """
        # using wrapped args to support type-checker typing hints
        wrapped: Callable = wrapped_args[0]
        args: list = wrapped_args[2] if len(wrapped_args) > 1 else []
        kwargs: dict = wrapped_args[3] if len(wrapped_args) > 2 else {}  # noqa: PLR2004

        def benchmark() -> Any:
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments.
            """

            before = dt.datetime.now(dt.UTC)
            data = wrapped(*args, **kwargs)
            after = dt.datetime.now(dt.UTC)
            delta = after - before
            if delta > dt.timedelta(
                microseconds=self.microseconds, milliseconds=self.milliseconds, seconds=self.seconds
            ):
                # wrapt always wraps a function/method, which has __name__; cast for ty
                function_name = cast('FunctionType', wrapped).__name__
                _logger.debug(f'function: "{function_name}", benchmark_time: "{delta}"')
            return data

        return benchmark()
