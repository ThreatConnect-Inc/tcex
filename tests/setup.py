import json
from setuptools import setup, find_packages

with open('install.json', 'r') as fh:
    version = json.load(fh)['programVersion']

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    description='Test the TcEx app.',
    name='tcex_tests',
    packages=find_packages(),
    version=version
)
