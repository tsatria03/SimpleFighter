# SimpleFighter map server.
#
# One program that both SERVES map downloads and RECEIVES moderated uploads.
# Replaces the old Caddy static server. Uses only Python's standard library,
# so nothing needs to be pip-installed - just a normal Python 3 install.
#
# Double-click this file to run it (it pauses on exit so you can read any
# error), or run "python sf_map_server.py" from a command prompt.
#
# ---------------------------------------------------------------------------
# EDIT THESE SETTINGS:
# ---------------------------------------------------------------------------
ROOT = r"C:\Users\Administrator\Desktop\SimpleFighter"  # the folder holding index.txt and the maps folder
PORT = 80                                               # 80 is the normal web port
UPLOAD_TOKEN = "vIOmjLLpBhn2J6aLoDcAVL8jNfY9e6nLVbYyEzwov8onZCa7McywBa78BzDzzgbJs3RAxmRlW3VRvy0T6j36zXtnWCjWpfQt0EIUWsqxjWhYlRQqP7vScI8Ptm1ChYPOCPgfZCsbLWr6fcdzlY0K10DGNA"                        # shared secret an uploading game must send - CHANGE THIS
MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024               # 2 GB per uploaded map
# ---------------------------------------------------------------------------

import os
import re
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

INDEX_LOCK = threading.Lock()  # guards writes to pending/index.txt against concurrent uploads

PUBLIC_DIR = os.path.join(ROOT, "maps", "public")                    # live, downloadable maps
PENDING_DIR = os.path.join(ROOT, "maps", "pending")                  # uploads waiting for your approval
INDEX_FILE = os.path.join(ROOT, "maps", "public_index.txt")          # the download list (served to players)
PENDING_INDEX_FILE = os.path.join(ROOT, "maps", "pending_index.txt") # the review queue (never served)

# A safe map filename: letters, digits, underscore, dot, dash; ends in .map; no spaces or path parts.
SAFE_NAME = re.compile(r"^[A-Za-z0-9_.\-]+\.map$")


def safe_map_name(raw):
    """Return a clean <name>.map filename, or None if it isn't safe."""
    name = os.path.basename(raw or "")
    if ".." in name:
        return None
    if not SAFE_NAME.match(name):
        return None
    return name


def update_pending_index(base, mode, size):
    """Add or refresh this map's line in pending_index.txt as name|mode|bytes - the
    review-queue mirror of the public index (same format the game's index uses; the
    name carries no .map). Re-uploading the same name replaces its line. Locked so
    simultaneous uploads don't clobber the file."""
    path = PENDING_INDEX_FILE
    with INDEX_LOCK:
        kept = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f.read().splitlines():
                    line = line.strip()
                    if line and line.split("|", 1)[0] != base:
                        kept.append(line)
        kept.append(base + "|" + mode + "|" + str(size))
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\r\n".join(kept))


class Handler(BaseHTTPRequestHandler):
    server_version = "SFMapServer/1.0"
    protocol_version = "HTTP/1.1"  # every response sets Content-Length, so keep-alive is safe; Poco's http client wants 1.1

    def _reply(self, code, body=b"", ctype="text/plain"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _serve_file(self, filepath, ctype):
        if not os.path.isfile(filepath):
            return self._reply(404, "Not found")
        try:
            size = os.path.getsize(filepath)
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(size))
            self.end_headers()
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client hung up mid-download; nothing to do

    # --- Downloads ---------------------------------------------------------
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/public_index.txt"):
            return self._serve_file(INDEX_FILE, "text/plain")
        if path.startswith("/maps/public/"):
            name = safe_map_name(urllib.parse.unquote(path[len("/maps/public/"):]))
            if name is None:
                return self._reply(404, "Not found")
            return self._serve_file(os.path.join(PUBLIC_DIR, name), "application/octet-stream")
        # Note: /maps/pending/ is deliberately NOT served - pending uploads are private until approved.
        return self._reply(404, "Not found")

    # --- Uploads (moderated: land in pending, never auto-published) ---------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/upload":
            return self._reply(404, "Not found")
        params = urllib.parse.parse_qs(parsed.query)
        token = (params.get("token") or [""])[0]
        name = (params.get("name") or [""])[0]
        mode = (params.get("mode") or [""])[0]
        if mode not in ("2d", "topdown", "3d"):
            mode = ""  # unknown mode stored blank; the dev can still approve it
        if token != UPLOAD_TOKEN:
            return self._reply(403, "Invalid upload token.")
        sname = safe_map_name(name)
        if sname is None:
            return self._reply(400, "Invalid map name.")

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0:
            return self._reply(400, "Empty upload.")
        if length > MAX_UPLOAD_BYTES:
            return self._reply(413, "That map is larger than the allowed limit.")

        os.makedirs(PENDING_DIR, exist_ok=True)
        dest = os.path.join(PENDING_DIR, sname)
        written = 0
        try:
            with open(dest, "wb") as out:
                remaining = length
                while remaining > 0:
                    chunk = self.rfile.read(min(65536, remaining))
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > MAX_UPLOAD_BYTES:
                        raise ValueError("exceeded size limit")
                    out.write(chunk)
                    remaining -= len(chunk)
        except Exception:
            if os.path.exists(dest):
                try:
                    os.remove(dest)
                except OSError:
                    pass
            return self._reply(500, "Upload failed.")

        update_pending_index(sname[:-4], mode, written)
        return self._reply(200, "OK")

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def set_window_title(title):
    """Set the console window title on Windows. Harmless no-op elsewhere."""
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def main():
    set_window_title("SimpleFighter map server")
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(PENDING_DIR, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True    # HTTP/1.1 keep-alive holds worker threads open; make them daemon so
    server.block_on_close = False   # closing the window (or Ctrl+C) kills the process instead of hanging on them
    print("SimpleFighter map server running on port %d." % PORT)
    print("Serving downloads from %s" % PUBLIC_DIR)
    print("Accepting uploads into  %s" % PENDING_DIR)
    print("Leave this window open. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\nServer error: %r" % e)
    input("\nPress Enter to close this window...")
