from setuptools import setup, find_packages

setup(
    author='ThreatConnect Inc',
    author_email='support@threatconnect.com',
    description='ThreatConnect Exchange Module',
    install_requires=[
        'hiredis==0.2.0',
        'jsonschema==2.5.1',
        'redis==2.10.5',
        'requests==2.11.1'
    ],
    license='Apache Liscense, Version 2',
    name='TcEx',
    packages=find_packages(),
    url='https://github.com/ThreatConnect-Inc/tcex',
    version='0.0.1'
)