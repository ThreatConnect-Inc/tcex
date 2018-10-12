# tcex - ThreatConnect Exchange App Framework

The ThreatConnect&trade; TcEx App Framework provides functionality for writing ThreatConnect Exchange Apps.

## Requirements

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

## Installation

**Using pip**

```
pip install tcex
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

1. Install the necessary requirements: `pip install -r test_requirements.py --upgrade`
2. Run `tclib` to create a `lib_2.7.12` directory from which your tests will pull their code
3. Configure the following environmental variables:
   - `API_ACCESS_ID` (e.g. `123456789987654321`)
   - `TC_API_PATH` (e.g. `https://sandbox.threatconnect.com/api`)
   - `API_DEFAULT_ORG` (e.g. `My Organization`)
   - `API_SECRET_KEY` (e.g. `abcdefg.....`)

    You can more details on how to setup environmental variables for TCEX [here](https://gitlab.com/fhightower-tc/tcex-playground#setup).

4. Run `cd tests/ && pytest tcex_tests.py --ignore=lib_2.7.12/`

## Contact

If you have any questions, bugs, or requests please contact support@threatconnect.com
