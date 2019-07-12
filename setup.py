import io
import os
import pathlib
import sys
from shutil import rmtree
from setuptools import setup, find_packages, Command


HERE_PATH = pathlib.Path(__file__).parent


NAME = 'krolib'
DESCRIPTION = 'DSL to handle complex schedules'
URL = 'https://github.com/nextiva/krolib'
EMAIL = 'roman.zayev@nextiva.com'
AUTHOR = 'Nextiva'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.0.0'


try:
    with io.open((HERE_PATH / 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(HERE_PATH / 'dist', ignore_errors=True)
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages(),
    license='Apache',
    url=URL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'python-dateutil==2.7.3',
        'pytz==2018.9',
        'toolz>=0.8.2',
        'tzlocal>=1.3',
        'voluptuous==0.11.5',
        'sphinx==2.0.1',
        'sphinx-rtd-theme==0.4.3',
    ],
    tests_require=[
        'pytest==3.2.5',
        'pytest-asyncio==0.9.0',
        'pytest-benchmark==3.1',
        'pytest-cov==2.5.1',
        'pytest-flakes==4.0.0',
        'pytest-pycodestyle==1.4.0',
    ],
    setup_requires=['pytest-runner'],
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)
