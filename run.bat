@echo off
setlocal enabledelayedexpansion 

set target_name=cai_rigtools

set blender_path=%1
if "%blender_path%"=="" (
  set blender_path=%BLENDER_PATH%
)
set pattern="[0-9]*\.[0-9]*"

for /d %%D in ("%blender_path%\*") do (
    set dirname=%%~nxD
    echo !dirname! | findstr /b /r "%pattern%" > nul
    if not errorlevel 1 (
        set blender_addons_path=!blender_path!\!dirname!\scripts\addons
    )
)

if "%blender_addons_path%"=="" (
    echo "Could not find Blender addons path"
    exit /b 1
)

set blender_executable=%blender_path%\blender.exe

set current_addon_folder=%~dp0/%target_name%

robocopy "%current_addon_folder%" "%blender_addons_path%/%target_name%" /mir /xo /ndl /njh /njs /np /ns /nc

%blender_executable% 

if %2==test (
    %blender_executable% --background --python "%blender_addons_path%/%target_name%/tests/run_tests.py"
) else (
    %blender_executable% --python-console
)

endlocal
