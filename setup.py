#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#

from setuptools import setup, find_packages

setup(
    name='jigna',
    version='0.0.1',
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
    package_data={'jigna': ['*.css', '*.png', '*.js',
                            'resources/bootstrap/css/*.css',
                            'resources/bootstrap/img/*.png',
                            'resources/bootstrap/js/*.js',
                            'resources/js/*.js']},
    zip_safe=False
)

