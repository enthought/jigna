:: Get pip
python get-pip.py

:: Install enpkg if not already installed
enpkg --version || pip install enstaller

:: Get core dependencies
enpkg traits pyside

:: Get dependencies for the web version
enpkg tornado

:: Get test dependencies
pip install nose selenium coverage

:: Develop the current package
python setup.py develop