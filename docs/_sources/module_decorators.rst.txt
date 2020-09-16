.. include:: <isonum.txt>
.. _module_decorators:

==================
Module: Decorators
==================

.. important:: App decorators have been updated with breaking changes in TcEx 2.0.

The ThreatConnect TcEx App Framework provides multiple Python decorators to help in setup of task that are common in Apps. Using multiple decorators on a single method is common.


Fail on Output
==============
The ``FailOnOutput()`` decorator is useful in decorating methods that should have a valid and/or specific output. The decorator can be enabled/disable directly by the App developer or based on a user input (e.g., Boolean input value in install.json).

The following example adds the ``FailOnOutput`` decorator to a method that takes a single IP Address input.  If the ``fail_on_false`` input is enabled and an invalid IP Address is provided the App will exit with the provided **fail_msg**. This decorator provides a decent amount of flexibility, provides consistent functionality, and reduces redundant code in the App.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    import ipaddress
    from tcex import FailOnOutput

    @FailOnOutput(
        fail_enabled='fail_on_false',  # references input value fail_on_false
        fail_msg='App failed due to invalid ip address',  # exit message
        fail_on=[False],  # invalid return values
        write_output=True,  # regardless of pass/fail write output variables
    )
    def is_ip_address(self, ip_address):
        """Return True if input is a valid ipv4 address."""
        try:
            ipaddress.ip_address('192.168.0.1')
        except ValueError:
            return False
        return True

Iterate On Arg
==============
The ``IterateOnArg()`` decorator is useful in decorating methods that process a single and array input. This decorator can be very useful in **action** based Apps. This decorator accepts validators and transforms in the same manner as ``ReadArg()``, please see that section for details.

The following example adds the ``IterateOnArg`` decorator to a method that takes a String or StringArray input and returns the value capitalized.  The decorator will call the method one time for each item in the input array (a single String input value would be automatically converted to an StringArray). If the ``fail_enabled`` input is enabled and any supplied validators fail, the App would then exit using the **fail_msg** string provided. This decorator provides a decent amount of flexibility, provides consistent functionality, and reduces redundant code in the App.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex import IterateOn

    @IterateOnArg(
        arg='colors',
        default=None,
        fail_enabled='fail_on_error,
        fail_msg='Failed to capitalize string input.',
        fail_on=['None' ''],
    )
    def capitalize(self, colors):
        """Return capitalized string."""
        return colors.capitalize()

On Exception
============
The ``OnException()`` decorator is useful in decorating methods that may have an exception that needs to be handled consistently.

The following example adds the ``OnException`` decorator to a method that processes an input.  The decorator will catch any **Exception** and write an exit message. If the ``fail_on_error`` input is enabled and an exception is caught, the App would then exit using the **exit_msg** string provided. This decorator provides a decent amount of flexibility, provides consistent functionality, and reduces redundant code in the App.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex import OnException

    @OnException(
        exit_msg='Failed to capitalize input.',
        exit_enabled='fail_on_error',
        write_output=False
    )
    def capitalize(self, colors):
        """Return capitalized string."""
        return colors.capitalize()

On Success
==========
The ``OnSuccess()`` decorator is useful in decorating methods with a predefined exit message on successfully execution.

The following example adds the ``OnSuccess`` decorator to a method that processes an input.  The decorator set the exit message of the App when the method successfully completes.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex import OnSuccess

    @OnSuccess(exit_msg='Successfully capitalized input.')
    def capitalize(self, colors):
        """Return capitalized string."""
        return colors.capitalize()

Output
======
The ``Output()`` decorator is useful in decorating methods that provide output that will be used during the ``write_output()`` method.

The following example adds the ``Output`` decorator to a method that processes an input.  The decorator will add the output of the method to the **attribute** provided to the decorator. This method is helpful when using the ``IterateOn()`` decorator. For each execution of the method the return data is appended/extended to the provided attribute. This decorator provides a decent amount of flexibility, provides consistent functionality, and reduces redundant code in the App.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex import Output

    def __init__(self):
        """Initialize class properties."""
        self.output_data = None

    @Output(attribute='output_data', overwrite=False)
    def capitalize(self, colors):
        """Return capitalized string."""
        return colors.capitalize()

Read Arg
========
The ``ReadArg()`` decorator is useful in decorating methods that use a user input.

The following example adds the ``ReadArg`` decorator to a method that takes a String.  The decorator will call the method passing the value of the **append_chars** input. If the ``fail_on_error`` input is enabled and the input matches a value in the **fail_on** array, the App would then exit using the **fail_msg** string provided. This decorator provides a decent amount of flexibility, provides consistent functionality, and reduces redundant code in the App.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex.decorators import ReadArg

    @ReadArg(
        arg='append_chars',
        fail_enabled='fail_on_error,
        fail_on=['None' ''],
    )
    def append(self, string, append_chars):
        """Return string with appended characters."""
        return f'{string}{append_chars}'

The ``ReadArg()`` decorator includes several built-in transforms that modify the value of the input and validators that perform checks on the input but do not change its value.

The following built-in transforms are available:

- to_bool
- to_float
- to_int

The following built-in validators are available:

- equals
- in_range
- greater_than
- greater_than_or_equal
- less_than
- less_than_or_equal
- not_in (this is equivalent to fail_on)

Transforms are run, in the order they are passed, before validators, which are also run in the order they are passed.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex.decorators import ReadArg

    @ReadArg(
        arg='confidence',
        fail_enabled='fail_on_error,
        fail_on=['None' ''],
        to_int=True,
        in_range={'min': 0, 'max': 100}
    )
    def append(self, confidence):
        """Return string with appended characters."""
        return f'{confidence}'

Custom validators and transforms can be defined using the ``validators`` and ``transforms`` arguments.  Both validators and transforms are callables that accept the input value and input name and raise a ``tcex.validators.ValidationError`` if the input is invalid.  Validators do not return a value, but transforms should return a new value for the input.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    from tcex.decorators import ReadArg
    from tcex.validators import ValidationError

    def to_email(value, arg_name):
        """This is a transform that takes a name and returns the associated email address"""
        name_to_email = {
            'Bob': 'bob@foo.com',
            'Sally': 'sally@foo.com'
        }

        if value in name_to_email:
            return name_to_email.get(value)

        raise ValidationError(f'no email found for {value}.')

    def is_valid_label(value, arg_name):
        valid_labels = ['High', 'Medium', 'Low']
        if value not in valid_labels:
            raise ValidationError(f'{arg_name} must be High, Medium, or Low')

    @ReadArg(
        arg='email_to',
        transforms=[to_email]
    )
    @ReadArg(
        arg='label',
        validators=[is_valid_label]
    )
    def append(self, email_to, label):
        """Return string with appended characters."""
        return f'{email_to}  - {label}'
