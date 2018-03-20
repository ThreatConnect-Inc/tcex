tcex - ThreatConnect Exchange App Framework
============================================

The ThreatConnect&trade; TcEx App Framework provides functionality for writing ThreatConnect Exchange Apps.

Requirements
-------------

Python requirements with known working version:
 * colorama 0.3.9 (https://pypi.python.org/pypi/colorama)
 * hvac 0.3.0 (https://pypi.python.org/pypi/hvac)
 * inflect 0.2.5 (https://pypi.python.org/pypi/inflect)
 * jsonschema 2.6.0 (https://pypi.python.org/pypi/jsonschema)
 * parsedatetime 2.4 (https://pypi.python.org/pypi/parsedatetime)
 * python-datetuil (https://pypi.python.org/pypi/python-dateutil)
 * pytz latest (https://pypi.python.org/pypi/pytz)
 * redis 2.10.6 (https://pypi.python.org/pypi/redis)
 * requests 2.18.4 (http://docs.python-requests.org/en/latest)
 * six 1.11.0 (https://pypi.python.org/pypi/six)
 * tzlocal 1.5.1 (https://pypi.python.org/pypi/tzlocal)

Installation
-------------
**Using pip**

```
pip install tcex
```

**Manually**

```
cd tcex
python setup.py install --force
```

Documentation
--------------
https://docs.threatconnect.com/en/latest/tcex/tcex.html

Release Notes
--------------
https://docs.threatconnect.com/en/latest/tcex/release_notes.html

Running Tests
-------------

To run the tests, run:

```
cd tests
tcrun
```

Running the tests requires some environment variables as shown in `tests/tcex.json`.

Contact
--------
If you have any questions, bugs, or requests please contact support@threatconnect.com