# Copyright (c) 2013 by Enthought, Inc.
# All rights reserved.

from setuptools import setup

setup(
    name='jigna',
    version='0.0.1',
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://bitbucket.org/agrawalprash/jigna',
    description='HTML/CSS/JS based frontend for Traits.',
    long_description=open('README.rst').read(),
    requires=['traits', 'pyface', 'Mako'],
    install_requires=['distribute'],
    packages=['jigna'],
    package_dir={'jigna':'jigna'},
    package_data={'jigna': ['resources/*.html', 'resources/*.js', 'templates/*.html', 'templates/*.js', 
                            'templates/*.mako']}
)

