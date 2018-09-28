"""Setup for TCEX Module"""
import re
import sys
from setuptools import setup, find_packages

with open('tcex/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__(?:\s+)?=(?:\s+)?[\'|\"]((?:[0-9]{1,3}(?:\.)?){1,3})[\'|\"]',
        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

install_requires = [
    'colorama>=0.3.9',
    'future',
    'hvac>=0.3.0',
    'inflect>=0.2.5',
    'jsonschema>=2.6.0',
    'parsedatetime',
    'python-dateutil>=2.6.1',
    'pytz',
    'redis>=2.10.6',
    'requests>=2.18.4',
    'six>=1.11.0',
    'tzlocal'
]
if sys.version_info < (3, ):
    install_requires.extend([
        'ipaddress'
    ])
scripts = [
    'bin/tcinit',
    'bin/tcinit.cmd',
    'bin/tclib',
    'bin/tclib.cmd',
    'bin/tcpackage',
    'bin/tcpackage.cmd',
    'bin/tcprofile',
    'bin/tcprofile.cmd',
    'bin/tcrun',
    'bin/tcrun.cmd'
]

setup(
    author='ThreatConnect (support@threatconnect.com)',
    author_email='support@threatconnect.com',
    description='ThreatConnect Exchange App Framework',
    download_url='https://github.com/ThreatConnect-Inc/tcex/tarball/{}'.format(version),
    install_requires=install_requires,
    license='Apache License, Version 2',
    name='tcex',
    packages=find_packages(),
    package_data={'': ['tcex_json_schema.json']},
    scripts=scripts,
    url='https://github.com/ThreatConnect-Inc/tcex',
    use_2to3=True,
    version=version
)
