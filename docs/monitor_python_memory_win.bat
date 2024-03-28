@echo off

:loop
set "total_memory_kb=0"
for /f "skip=1 tokens=*" %%a in (
'wmic process where "Name like '%%Python%%'" get WorkingSetSize ^| findstr /r "[0-9]"'
) do (
    set "memory_bytes=%%a"
    set /a "memory_kb=memory_bytes / 1024"
    set /a "total_memory_kb+=memory_kb"
)

rem Output total memory usage in GB
echo Total memory usage of Python processes: %total_memory_kb% KB

timeout /t 1 >nul
goto loop
