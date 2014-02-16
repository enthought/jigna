#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#

import os.path
from setuptools import setup, find_packages

data = {}
execfile(os.path.join('jigna', '__init__.py'), data)

setup(
    name='jigna',
    version=data['__version__'],
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://github.com/enthought/jigna',
    description='HTML frontend for Traits models.',
    long_description=open('README.rst').read(),
    requires=['traits', 'pyface'],
    install_requires=['distribute'],
    packages=find_packages(),
    package_dir={'jigna':'jigna'},
    include_package_data=True,
    package_data={'jigna': ['resources/js/*.js']},
    zip_safe=False
)
