# -*- coding: utf-8 -*-
"""App Decorators Module."""
# standard library
import datetime

# third-party
import wrapt


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

        def benchmark(app, *args, **kwargs):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """

            # before = float('{time.clock():.4f}')
            before = datetime.datetime.now()
            data = wrapped(*args, **kwargs)
            # after = float('{time.clock():.4f}')
            after = datetime.datetime.now()
            app.tcex.log.debug(
                f'function: "{self.__class__.__name__}", benchmark_time: "{after - before}"'
            )
            return data

        return benchmark(instance, *args, **kwargs)
