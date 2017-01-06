from setuptools import setup, find_packages

version = '0.0.2'
setup(
    author='ThreatConnect Inc',
    author_email='support@threatconnect.com',
    description='ThreatConnect Exchange App Framework',
    download_url='https://github.com/ThreatConnect-Inc/tcex/tarball/{}'.format(version),
    install_requires=[
        'hiredis==0.2.0',
        'jsonschema==2.5.1',
        'redis==2.10.5',
        'requests==2.11.1'
    ],
    license='Apache License, Version 2',
    name='tcex',
    packages=find_packages(),
    package_data={'': ['tcex_json_schema.json']},
    url='https://github.com/ThreatConnect-Inc/tcex',
    use_2to3=True,
    # use_2to3_exclude_fixers=['lib2to3.fixes.fix_print'],
    version=version
)

