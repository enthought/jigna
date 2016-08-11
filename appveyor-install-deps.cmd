"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

rem install python packages
pip install --cache-dir c:/temp traits
pip install --cache-dir c:/temp pyside
pip install --cache-dir c:/temp tornado
pip install --cache-dir c:/temp nose
pip install --cache-dir c:/temp selenium
pip install --cache-dir c:/temp coverage
pip install --cache-dir c:/temp mock

rem install jigna
pip setup.py develop
