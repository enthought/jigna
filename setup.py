# Copyright (c) 2013 by Enthought, Inc.
# All rights reserved.

from setuptools import setup, find_packages

setup(
    name='jigna',
    version='0.0.1',
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://bitbucket.org/agrawalprash/jigna',
    description='HTML/CSS/JS based frontend for Traits.',
    long_description=open('README.rst').read(),
    requires=['traits', 'pyface', 'Mako', 'traitsui', 'tornado', 'jinja2', 'beautifulsoup4'],
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

