"""App Decorators Module."""
# standard library
import datetime
import logging
from typing import Optional

# third-party
import wrapt

# get tcex logger
logger = logging.getLogger('tcex')


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
        microseconds: Optional[int] = 0,
        milliseconds: Optional[int] = 0,
        seconds: Optional[int] = 0,
    ):
        """Initialize Class properties."""
        self.microseconds = microseconds
        self.milliseconds = milliseconds
        self.seconds = seconds

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
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

        def benchmark(_, *args, **kwargs):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """

            before = datetime.datetime.now()
            data = wrapped(*args, **kwargs)
            after = datetime.datetime.now()
            delta = after - before
            if delta > datetime.timedelta(
                microseconds=self.microseconds, milliseconds=self.milliseconds, seconds=self.seconds
            ):
                logger.debug(f'function: "{wrapped.__name__}", benchmark_time: "{delta}"')
            return data

        return benchmark(instance, *args, **kwargs)
