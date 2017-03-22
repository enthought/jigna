#
# (C) Copyright 2013-2017 Enthought, Inc., Austin, TX
# All right reserved.
#

import os.path
from setuptools import setup, find_packages

data = {}
fname = os.path.join('jigna', '__init__.py')
exec(compile(open(fname).read(), fname, 'exec'), data)

requires = ['traits', 'tornado']
pyside = requires + ['pyside']
test = pyside + ['nose', 'mock', 'coverage', 'selenium']

with open('README.rst') as fp:
    long_desc = fp.read()


setup(
    name='jigna',
    version=data['__version__'],
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://github.com/enthought/jigna',
    license='BSD',
    description='HTML frontend for Traits models.',
    long_description=long_desc,
    packages=find_packages(),
    package_dir={'jigna': 'jigna'},
    include_package_data=True,
    package_data={'jigna': ['js/dist/*.js']},
    install_requires=requires,
    extras_require={
        'pyside': pyside,
        'test': test,
    },
    classifiers=[
        c.strip() for c in """\
        Development Status :: 4 - Beta
        Environment :: Web Environment
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS :: MacOS X
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Programming Language :: JavaScript
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        Topic :: Software Development :: User Interfaces
        """.splitlines() if len(c.split()) > 0
    ],
    zip_safe=False
)
