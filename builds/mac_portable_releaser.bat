@echo off
set GAME=SimpleFighter
set PASSWORD=SpfBuilder

set MAC_SOURCE=..\releases\mac\SimpleFighter_mac_portable_password_is_SpfBuilder\sf.app

echo.
echo Building Mac portable ZIP archive...
echo.

"C:\Program Files\7-Zip\7z.exe" a -tzip "%GAME%_mac_portable_password_is_%PASSWORD%.zip" "%MAC_SOURCE%" -mx=9 -mm=Deflate -mfb=128 -mmt=12 -p%PASSWORD%

echo.
echo Mac portable build complete.
pause
