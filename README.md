tcex - ThreatConnect Exchange Modules
====================================

The tcex python project is a part of the ThreatConnect&trade; SDK.  This module provides methods to help build ThreatConnect Standard Apps as well as Playbook Apps.  The module also provides methods to assist in utilizing the ThreatConnect Version 2 REST API.

Requirements
------
The tcex project can run under Python 2.7.x.

Python requirements with known working version:
 * Requests 2.11.1 module (http://docs.python-requests.org/en/latest/).
 * hiredis 0.2.0 (https://github.com/redis/hiredis-py)
 * jsonschema 2.5.1 (https://pypi.python.org/pypi/jsonschema)
 * redis 2.10.5 (https://pypi.python.org/pypi/redis)

Authentication
--------------
When running from the integrations server valid API credentials for the ThreatConnect instance are required.  When running under the ThreatConnect main instance a token will be provided for authentication.

Installation
-----
Using pip

```
pip install tcex
```

Manually

```
cd tcex
python setup.py install --force
```

Documentation
-----
Coming soon.

Contact
-----
If you have any questions, bugs, or requests please contact support@threatconnect.com


Writing an Standard App
-----


API Logging
-----


Message TC
-----
Every app should write to `message_tc()` on all success and failures.


Exit
-----
The `tcex.exit()` method should always be called at the end of successful or failed execution.