@echo off
setlocal EnableExtensions
chcp 65001 >nul

cd /d "%~dp0"
set "EXIT_CODE=0"
set "ARGS=%*"

title TKAutoFisher
python -c "print('='*40)"
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape'))" "         TKAutoFisher \u542f\u52a8\u5668"
python -c "print('='*40)"
echo.

if not "%~1"=="" goto run

python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape'))" "[1] \u6b63\u5e38\u542f\u52a8 (\u9ed8\u8ba4\u914d\u7f6e)"
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape'))" "[2] \u68c0\u67e5\u6a21\u5f0f (\u9ed8\u8ba4\u914d\u7f6e)"
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape'))" "[3] \u9000\u51fa"
echo.
choice /c 123 /n /m "> "

if errorlevel 3 goto end
if errorlevel 2 set "ARGS=--check-mode --profile default" & goto run
if errorlevel 1 set "ARGS=--profile default" & goto run

:run
where python >nul 2>nul
if errorlevel 1 goto py_not_found

python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape') + sys.argv[2])" "[\u4fe1\u606f] \u6267\u884c\u547d\u4ee4: " "python main.py %ARGS%"
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape') + sys.argv[2])" "[\u4fe1\u606f] \u5f53\u524d\u76ee\u5f55: " "%CD%"
echo.

python "main.py" %ARGS%
set "EXIT_CODE=%ERRORLEVEL%"
echo.

if "%EXIT_CODE%"=="0" goto success
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape') + sys.argv[2])" "[\u9519\u8bef] \u6267\u884c\u5931\u8d25, \u9000\u51fa\u7801: " "%EXIT_CODE%"
goto endpause

:success
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape'))" "[\u4fe1\u606f] \u6267\u884c\u5b8c\u6210, \u9000\u51fa\u7801: 0"
goto endpause

:py_not_found
python -c "import sys;print(sys.argv[1].encode('utf-8').decode('unicode_escape'))" "[\u9519\u8bef] \u672a\u627e\u5230 Python\uff0c\u8bf7\u5148\u5b89\u88c5\u5e76\u52a0\u5165 PATH\u3002"
set "EXIT_CODE=1"

:endpause
echo.
pause
exit /b %EXIT_CODE%

:end
exit /b 0
