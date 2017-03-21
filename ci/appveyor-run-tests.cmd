"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

mkdir testrun
copy .coveragerc testrun/
cd testrun

coverage run -m nose.core -v jigna
if %errorlevel% neq 0 exit /b %errorlevel%
coverage report
