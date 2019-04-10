from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = 2.0.0

setup(
    install_requires = ['pytest',
                        'sphinx==1.8.5',
                        'pycodestyle',
                        'pytest-cov',
                        'mock',
                        'configparser',
                        'pydocstyle',
                        'coveralls',
                        'cothread'],
    dependency_links = [
     "https://github.com/dls-controls/cothread.git/repo/tarball/master#egg=package-1.0",
    ],
    name = 'pyburt',
    version = version,
    description = 'Module',
    author = 'ia',
    author_email = 'ito.alcuaz@diamond.ac.uk',
    packages = ['pyburt'],
    include_package_data = True,
    zip_safe = False
    )
