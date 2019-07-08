@echo OFF
REM="""
setlocal
set PythonExe=""
set PythonExeFlags=

for %%i in (cmd bat exe) do (
    for %%j in (python.%%i) do (
        call :SetPythonExe "%%~$PATH:j"
    )
)
for /f "tokens=2 delims==" %%i in ('assoc .py') do (
    for /f "tokens=2 delims==" %%j in ('ftype %%i') do (
        for /f "tokens=1" %%k in ("%%j") do (
            call :SetPythonExe %%k
        )
    )
)
%PythonExe% -x %PythonExeFlags% "%~f0" %*
exit /B %ERRORLEVEL%
goto :EOF

:SetPythonExe
if not ["%~1"]==[""] (
    if [%PythonExe%]==[""] (
        set PythonExe="%~1"
    )
)
goto :EOF
"""

import subprocess
import sys

def main():
    # Update system arguments
    sys.argv[0] = sys.argv[0].replace('.cmd', '')
    python_exe = sys.executable
    sys.argv.insert(0, python_exe)

    # Make sure to exit with the return value from the subprocess call
    ret = subprocess.call(sys.argv)
    sys.exit(ret)

if __name__ == '__main__':
    sys.exit(main())
