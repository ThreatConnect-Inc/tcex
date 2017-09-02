import re
from setuptools import setup, find_packages

with open('tcex/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__(?:\s+)?=(?:\s+)?[\'|\"]((?:[0-9]{1,3}(?:\.)?){1,3})[\'|\"]',
        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    author='ThreatConnect (support@threatconnect.com)',
    author_email='support@threatconnect.com',
    description='ThreatConnect Exchange App Framework',
    download_url='https://github.com/ThreatConnect-Inc/tcex/tarball/{}'.format(version),
    install_requires=[
        'colorama==0.3.9',
        'hvac==0.2.17',  # this feature will be deprecate in future release
        'inflect==0.2.5',
        'jsonschema==2.6.0',
        'python-dateutil==2.6.1',
        'redis==2.10.6',
        'requests==2.18.4'
    ],
    license='Apache License, Version 2',
    name='tcex',
    packages=find_packages(),
    package_data={'': ['tcex_json_schema.json']},
    scripts=[
        'bin/tcdata',
        'bin/tcdata.cmd',
        'bin/tclib',
        'bin/tclib.cmd',
        'bin/tcpackage',
        'bin/tcpackage.cmd',
        'bin/tcprofile',
        'bin/tcprofile.cmd',
        'bin/tcrun',
        'bin/tcrun.cmd'
    ],
    url='https://github.com/ThreatConnect-Inc/tcex',
    use_2to3=True,
    version=version
)
