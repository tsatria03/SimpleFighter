@echo off
REM Regenerates index.txt for the SimpleFighter in-game map downloader.
REM Place this in the folder that holds the "maps" subfolder. It lists the
REM .map files inside maps\ (one filename per line, extension included) and
REM writes index.txt next to itself. Run it after adding or removing maps.
cd /d "%~dp0"
dir /b maps\*.map > index.txt
echo Done. index.txt now lists the .map files in the maps folder.
pause
