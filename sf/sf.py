import os
import sys
import subprocess
import ctypes

# Launch SimpleFighter. The .nvgt source lives in src/, but the assets (lib, sounds,
# data, docks) live here in sf/, so we run with cwd set to this folder: every
# cwd-relative path in the game (lib/..., sounds/..., data/..., docks/...) then
# resolves against sf/. CREATE_NO_WINDOW gives nvgt no console; the launcher spawns
# and exits, so its own console only flashes. The game opens its own NVGT window.

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(HERE, "..", "src", "sf.nvgt"))
VERSION_TXT = os.path.normpath(os.path.join(HERE, "..", "build", "version.txt"))
VERSION_NVGT = os.path.normpath(os.path.join(HERE, "..", "src", "includes", "version.nvgt"))
NVGT = r"C:\nvgt2\nvgtw.exe"


def fail(message):
    ctypes.windll.user32.MessageBoxW(0, message, "SimpleFighter launcher", 0x10)
    sys.exit(1)


def sync_version():
    # build/version.txt is the single source of truth for the version; mirror it into
    # version.nvgt before launch so the game runs as whatever version.txt says. Only
    # rewrite when the value actually changed, and keep the file CRLF like the rest of
    # the repo. A missing or empty version.txt just leaves version.nvgt untouched.
    try:
        with open(VERSION_TXT, "r", encoding="utf-8") as f:
            version = f.read().strip()
    except OSError:
        return
    if not version:
        return
    line = 'string version = "%s";\r\n' % version
    try:
        with open(VERSION_NVGT, "r", encoding="utf-8") as f:
            if f.read() == line:
                return
    except OSError:
        pass
    try:
        with open(VERSION_NVGT, "w", newline="", encoding="utf-8") as f:
            f.write(line)
    except OSError as error:
        fail("Failed to sync the version into version.nvgt:\n" + str(error))


if not os.path.isfile(NVGT):
    fail("Could not find the NVGT runtime at:\n" + NVGT)
if not os.path.isfile(SCRIPT):
    fail("Could not find the SimpleFighter script at:\n" + SCRIPT)

sync_version()

try:
    subprocess.Popen(
        [NVGT, SCRIPT],
        cwd=HERE,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
except Exception as error:
    fail("Failed to start SimpleFighter:\n" + str(error))
