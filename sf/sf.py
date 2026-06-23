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
NVGT = r"C:\nvgt2\nvgtw.exe"


def fail(message):
    ctypes.windll.user32.MessageBoxW(0, message, "SimpleFighter launcher", 0x10)
    sys.exit(1)


if not os.path.isfile(NVGT):
    fail("Could not find the NVGT runtime at:\n" + NVGT)
if not os.path.isfile(SCRIPT):
    fail("Could not find the SimpleFighter script at:\n" + SCRIPT)

try:
    subprocess.Popen(
        [NVGT, SCRIPT],
        cwd=HERE,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
except Exception as error:
    fail("Failed to start SimpleFighter:\n" + str(error))
