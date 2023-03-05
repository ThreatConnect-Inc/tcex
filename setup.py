"""Setup for TcEx Module."""
# standard library
import os

# third-party
from setuptools import find_packages, setup

metadata = {}
metadata_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tcex', '__metadata__.py')
with open(
    metadata_file,
    encoding='utf-8',
) as f:
    exec(f.read(), metadata)  # nosec; pylint: disable=exec-used

if not metadata:
    raise RuntimeError(f'Could not load metadata file ({metadata_file}).')

with open('README.md') as f:
    readme = f.read()

dev_packages = [
    'bandit',
    'black',
    'codespell',
    'deepdiff',
    'fakeredis',
    'flake8',
    'isort',
    'mako',
    'pre-commit',
    'pydocstyle',
    'pylint',
    'pyright',
    'pytest',
    'pytest-cov',
    'pytest-html',
    'pytest-ordering',
    'pytest-xdist',
    'pyupgrade',
]


setup(
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Security',
    ],
    description=metadata['__description__'],
    download_url=metadata['__download_url__'],
    extras_require={'dev': dev_packages, 'develop': dev_packages, 'development': dev_packages},
    include_package_data=True,
    install_requires=[
        'arrow',
        'astunparse',
        'colorama',
        'inflect',
        'jmespath',
        'paho-mqtt',
        'pyaes',
        'pydantic',
        'python-dateutil',
        'pyyaml',
        'redis',
        'requests',
        'semantic_version',
        'stdlib-list',
        'tinydb',
        'typer',
        'wrapt',
    ],
    license=metadata['__license__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    name=metadata['__package_name__'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_dir={'tcex': 'tcex'},
    project_urls={
        'Documentation': 'https://github.com/ThreatConnect-Inc/tcex',
        'Source': 'https://github.com/ThreatConnect-Inc/tcex',
    },
    python_requires='>=3.11',
    scripts=[
        'bin/tcex',
    ],
    url=metadata['__url__'],
    version=metadata['__version__'],
    zip_safe=True,
)
