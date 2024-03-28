@echo off
setlocal enabledelayedexpansion

:loop
set "total_memory_kb=0"
for /f "skip=1 tokens=*" %%a in (
'wmic process where "Name like '%%Python%%'" get WorkingSetSize ^| findstr /r "[0-9]"'
) do (
    set /a "memory_kb=%%a / 1024"
    set /a "total_memory_kb+=memory_kb"
)
echo Total memory usage of Python processes: %total_memory_kb% KB
timeout /t 1 >nul
goto loop
