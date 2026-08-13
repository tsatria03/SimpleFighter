import os
import re
import sys
import subprocess
import tempfile
import ctypes

# Launch SimpleFighter. The .nvgt source lives in src/, but the assets (lib, sounds,
# data, docks) live here in sf/, so we run with cwd set to this folder: every
# cwd-relative path in the game (lib/..., sounds/..., data/..., docks/...) then
# resolves against sf/. We run the console build nvgt.exe (not the windowless nvgtw.exe)
# with CREATE_NO_WINDOW so no console window appears, yet NVGT's compile output still
# reaches a log we can capture -- letting us surface compile errors to errors.txt
# instead of NVGT's own popup. The game opens its own NVGT window.

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(HERE, "..", "src", "sf.nvgt"))
VERSION_TXT = os.path.normpath(os.path.join(HERE, "..", "build", "version.txt"))
VERSION_NVGT = os.path.normpath(os.path.join(HERE, "..", "src", "includes", "version.nvgt"))
NVGT = r"C:\nvgt2\nvgt.exe"
# How long (seconds) to watch the game for an early exit before assuming it compiled and detaching. A failed
# compile bails out within a second or two; a clean compile keeps running the game, so this is also the launch
# delay on a successful start. Raise it if compilation ever takes longer than this on a slow machine.
COMPILE_WAIT = 5
# Where a compile-error report is written: the sf/ folder next to this launcher, so it's always in the same place.
# Created only on a failed launch (a clean launch removes any stale copy first), so an absent or empty errors.txt
# means "no errors".
ERRORS_PATH = os.path.join(HERE, "errors.txt")


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


# Hide our own console window: because of the watch-for-compile-errors wait below, the launcher lives for a few
# seconds, and without this its cmd window would sit on screen that whole time (the game window is already up).
# fail()'s MessageBox is a separate GUI dialog, so errors still show. No-op if launched without a console (pythonw).
_console = ctypes.windll.kernel32.GetConsoleWindow()
if _console:
    ctypes.windll.user32.ShowWindow(_console, 0)  # SW_HIDE

if not os.path.isfile(NVGT):
    fail("Could not find the NVGT runtime at:\n" + NVGT)
if not os.path.isfile(SCRIPT):
    fail("Could not find the SimpleFighter script at:\n" + SCRIPT)

sync_version()

# Clear any errors.txt left by a previous failed launch, so a clean run leaves none behind.
try:
    os.remove(ERRORS_PATH)
except OSError:
    pass

# Capture NVGT's output (where it prints compile errors) to a temp log, then watch briefly: a failed compile
# exits fast with a non-zero code, while a clean compile keeps running the game and never exits on its own.
log_fd, log_path = tempfile.mkstemp(prefix="simplefighter_", suffix=".log")
log_file = os.fdopen(log_fd, "wb")
try:
    proc = subprocess.Popen(
        [NVGT, SCRIPT],
        cwd=HERE,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
except Exception as error:
    log_file.close()
    try:
        os.remove(log_path)
    except OSError:
        pass
    fail("Failed to start SimpleFighter:\n" + str(error))

try:
    code = proc.wait(timeout=COMPILE_WAIT)
except subprocess.TimeoutExpired:
    # Still running after the wait => it compiled and the game window is up. Detach and leave it running; NVGT
    # keeps its own inherited handle to the temp log, which lingers harmlessly in the temp folder for the session.
    log_file.close()
    sys.exit(0)

# The process exited within the watch window. A non-zero code means it never got past compiling/startup, so
# surface the captured output to errors.txt (in the sf/ folder) and tell the user.
log_file.close()
if code != 0:
    try:
        with open(log_path, "rb") as f:
            raw = f.read().decode("utf-8", "replace")
        # NVGT's text-mode stdout doubles newlines when redirected to a file (\r\n -> \r\r\n). Strip the \r,
        # collapse the resulting runs of blank lines to a single blank between records, and split the leading
        # "Compilation error:" prefix onto its own line so every record reads uniformly, starting with "file:".
        details = re.sub(r"\n{2,}", "\n\n", raw.replace("\r", ""))
        details = details.replace("Compilation error: ", "Compilation error:\n").strip()
    except OSError:
        details = ""
    body = details if details else "(SimpleFighter exited with code %d but printed no output)" % code
    try:
        with open(ERRORS_PATH, "w", encoding="utf-8") as f:
            f.write(body + "\n\n")  # trailing blank line after the last record, matching the blanks between records
    except OSError:
        pass
    try:
        os.remove(log_path)
    except OSError:
        pass
    fail("SimpleFighter failed to start (exit code %d).\nDetails written to:\n%s" % (code, ERRORS_PATH))

# Exited cleanly within the window (ran and closed right away). Nothing to report; tidy up the temp log.
try:
    os.remove(log_path)
except OSError:
    pass
