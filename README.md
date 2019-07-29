# tcex - ThreatConnect Exchange App Framework

The ThreatConnect&trade; TcEx App Framework provides functionality for writing ThreatConnect Exchange Apps.

## Requirements

 * colorama (https://pypi.python.org/pypi/colorama)
 * future (https://pypi.org/project/future/)
 * hvac (https://pypi.python.org/pypi/hvac)
 * inflect (https://pypi.python.org/pypi/inflect)
 * jsonschema (https://pypi.python.org/pypi/jsonschema)
 * parsedatetime (https://pypi.python.org/pypi/parsedatetime)
 * python-datetuil (https://pypi.python.org/pypi/python-dateutil)
 * pytz (https://pypi.python.org/pypi/pytz)
 * redis (https://pypi.python.org/pypi/redis)
 * requests (http://docs.python-requests.org/en/latest)
 * six (https://pypi.python.org/pypi/six)
 * stdlib-list (https://pypi.org/project/stdlib-list/)
 * tzlocal (https://pypi.python.org/pypi/tzlocal)

### Development Requirements

 * deepdiff (https://pypi.org/project/deepdiff/)
 * jmespath (https://pypi.org/project/jmespath/)
 * mako (https://pypi.org/project/mako/)
 * pytest (https://pypi.org/project/pytest/)
 * pytest-cov (https://pypi.org/project/pytest-cov/)

## Installation

**Using pip**

```
pip install tcex
pip install tcex[development]
```

**Manually**

```
cd tcex
python setup.py install --force
```

## Documentation

https://docs.threatconnect.com/en/latest/tcex/tcex.html

## Release Notes

https://docs.threatconnect.com/en/latest/tcex/release_notes.html

## Running Tests

All tests should be run in python2. The instructions below assume you have python2 on your system and have tcex installed.

To run the tests, you will need to:

0. Move into `tests` directory (`cd tests`)
1. Configure the following environmental variables:
   - `API_ACCESS_ID` (e.g. `123456789987654321`)
   - `TC_API_PATH` (e.g. `https://sandbox.threatconnect.com/api`)
   - `API_DEFAULT_ORG` (e.g. `My Organization`)
   - `API_SECRET_KEY` (e.g. `abcdefg.....`)
2. Run `pytest` (you may have to run `python2.7 -m pytest` depending on how your system is setup)

## Contact

If you have any questions, bugs, or requests please contact support@threatconnect.com
