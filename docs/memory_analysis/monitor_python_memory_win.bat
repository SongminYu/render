@echo off

:loop
set "total_memory_mb=0"
for /f "skip=1 tokens=*" %%a in (
'wmic process where "Name like '%%Python%%'" get WorkingSetSize ^| findstr /r "[0-9]"'
) do (
    set "memory_bytes=%%a"
    set /a "memory_mb=memory_bytes / 1024 / 1024"
    set /a "total_memory_mb+=memory_mb"
)

echo Total memory usage of Python processes: %total_memory_mb% MB

timeout /t 1 >nul
goto loop
