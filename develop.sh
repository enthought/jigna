#!/bin/bash

# Get pip
python get-pip.py

# Install enstaller (which contains enpkg)
if ! [ -x "enpkg" ]; then
    pip install enstaller
fi

# Get core dependencies
enpkg traits pyside

# Get dependencies for the web version
enpkg tornado

# Get test dependencies
pip install nose selenium coverage

# Develop the current package
python setup.py develop