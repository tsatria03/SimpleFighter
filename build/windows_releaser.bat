@echo off
set GAME=SimpleFighter
set PASSWORD=SpfBuilder

set WIN_SOURCE=..\releases\windows\SimpleFighter_windows_portable_password_is_SpfBuilder\sf

echo.
echo Building Windows portable 7z archive...
echo.

"C:\Program Files\7-Zip\7z.exe" a -t7z "%GAME%_windows_portable_password_is_%PASSWORD%.7z" "%WIN_SOURCE%" -mx=9 -m0=LZMA2 -md=64m -mfb=64 -ms=on -mmt=12 -p%PASSWORD% -mhe=on

echo.
echo Windows portable build complete.
pause
