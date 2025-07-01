@echo off
echo Copying media files...

REM Create media directory if it doesn't exist
if not exist "media" mkdir media

REM Copy event images
if exist "main\static\main\images\events" (
    if not exist "media\events" mkdir media\events
    xcopy /E /Y "main\static\main\images\events\*" "media\events\"
    echo Copied event images
)

REM Copy news images
if exist "main\static\main\images\news" (
    if not exist "media\news" mkdir media\news
    xcopy /E /Y "main\static\main\images\news\*" "media\news\"
    echo Copied news images
)

REM Copy project images
if exist "main\static\main\images\projects" (
    if not exist "media\projects" mkdir media\projects
    xcopy /E /Y "main\static\main\images\projects\*" "media\projects\"
    echo Copied project images
)

echo Media files copied successfully!
pause
