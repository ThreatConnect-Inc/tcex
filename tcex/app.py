#!/usr/bin/env python

""" standard """
import sys

""" third-party """
""" custom """
from tcex import TcExLocal

"""
Copy this python script to your app base directory to use the tcex_local module.

Example Usage:

Install all the required libraries defined in setup.py.  These will be the same packages
with the same version that will get *packaged* with the app.

./app.py --lib

Package the app for installation on the ThreatConnect platform.  Optionally you can pass
the *--collection* flag that will bundle multiple apps into one "App Collection".  The script
will also move the app package to another folder using the *--zip_out* flag.

./app.py --package
./app.py --package --collection
./app.py --package --collection --zip_out /opt/threatconnect/app/bundled/

Validate the application's install.json file.  The validate command is automatically executed
when packaging an app.  A configuration file name can be passed to the script using
the *--config* argument.  By default the script will check the *install.json* file.

./app.py --validate
./app.py --validate --install_json myapp1.install.json

Run the script locally. The tcex_local module will use the tc.json file to generate
the CLI args required by the script.  Typically an app would ship with a tc.json.template
file that provides example CLI args for the app to be run locally.  The config file supports
multiple configuration for different test/use cases with the default case being named "default".
Use the *--test* arg to pass a selected test.

./app.py --run
./app.py --run --profile Test1
./app.py --run --config tcex.json --group MyGroup
"""

print('Python Version: {}.{}.{}'.format(
    sys.version_info.major, sys.version_info.minor, sys.version_info.micro))

tcex_local = TcExLocal()
args = tcex_local.args

if args.lib:
    tcex_local.gen_lib()
elif args.package:
    tcex_local.package()
elif args.run:
    tcex_local.run()
elif args.validate:
    tcex_local.validate(args.install_json)
