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
ADMIN_TOKEN = "y1nIO3RowtqLThgHzrXSjB9TaNLzwdNBxrLzB7w4v5T0kXhQFmc0UfF1uuMW6aPruGmNT1baRoQwydGhIRuru8wsQv9bMcadfXKxc0BjYian0SvNlEC7nawYfGMZm8JhbeEk7iOXs5gL9bNBJH7EqQNfOeS3fvSUdh7HrlsVLFEduXryZpCUng5o4EOghutE7F1YQP52gcyPYHN2f3Dc2PGpCEvoLBuDRJoyquBJenEwzcT46weijDmYTaCx2EsrT"  # SEPARATE, private admin secret for approving/rejecting maps - never put this in any src/*.nvgt file
MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024               # 2 GB per uploaded map
# HTTPS for the ADMIN PANEL only (downloads/uploads stay on plain HTTP). Point these
# at a certificate + private key (PEM) and the panel is served over HTTPS on 443;
# visiting the panel over http then redirects to https. Leave BLANK to run HTTP only.
# A self-signed cert is fine here since only your own browser uses the panel:
#   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/CN=reality-breaker-studios.net"
CERT_FILE = ""                                          # e.g. r"C:\Users\Administrator\Desktop\SimpleFighter\cert.pem"
KEY_FILE = ""                                           # e.g. r"C:\Users\Administrator\Desktop\SimpleFighter\key.pem"
HTTPS_PORT = 443
# ---------------------------------------------------------------------------

import base64
import os
import re
import ssl
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


# --- index file helpers (name|mode|bytes lines, CRLF) ----------------------
def read_index_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f.read().splitlines() if ln.strip()]


def write_index_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines))


def _base_of(line):
    return line.split("|", 1)[0]


def index_upsert(lines, base, mode, size):
    """Replace any existing line for base, then append base|mode|size."""
    kept = [ln for ln in lines if _base_of(ln) != base]
    kept.append("%s|%s|%s" % (base, mode, size))
    return kept


def index_remove(lines, base):
    return [ln for ln in lines if _base_of(ln) != base]


def index_lookup(lines):
    """base -> (mode, size) from name|mode|bytes lines."""
    out = {}
    for ln in lines:
        parts = ln.split("|")
        base = parts[0]
        mode = parts[1] if len(parts) > 1 else ""
        size = parts[2] if len(parts) > 2 else ""
        out[base] = (mode, size)
    return out


def update_pending_index(base, mode, size):
    """Add or refresh this map's line in pending_index.txt as name|mode|bytes - the
    review-queue mirror of the public index (same format the game's index uses; the
    name carries no .map). Re-uploading the same name replaces its line. Locked so
    simultaneous uploads don't clobber the file."""
    with INDEX_LOCK:
        lines = read_index_lines(PENDING_INDEX_FILE)
        write_index_lines(PENDING_INDEX_FILE, index_upsert(lines, base, mode, str(size)))


# --- moderation (admin-only: list the queue, approve into public, reject) ---
def list_pending_maps():
    """The review queue as name|mode|bytes lines, built off the REAL .map files in
    pending (authoritative - a missing or stale index line can't hide a map). Mode
    comes from pending_index.txt, size from disk."""
    if not os.path.isdir(PENDING_DIR):
        return []
    idx = index_lookup(read_index_lines(PENDING_INDEX_FILE))
    out = []
    for fname in sorted(os.listdir(PENDING_DIR)):
        if not SAFE_NAME.match(fname):
            continue  # skip the index or any stray non-map file
        path = os.path.join(PENDING_DIR, fname)
        if not os.path.isfile(path):
            continue
        base = fname[:-4]
        mode = idx.get(base, ("", ""))[0]
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0
        out.append("%s|%s|%s" % (base, mode, size))
    return out


def approve_map(base):
    """Move pending/<base>.map into public and its line into public_index.txt.
    Returns True on success, False if the pending map isn't there."""
    src = os.path.join(PENDING_DIR, base + ".map")
    dest = os.path.join(PUBLIC_DIR, base + ".map")
    if not os.path.isfile(src):
        return False
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with INDEX_LOCK:
        mode = index_lookup(read_index_lines(PENDING_INDEX_FILE)).get(base, ("", ""))[0]
        try:
            size = os.path.getsize(src)
        except OSError:
            size = 0
        # Move the file first; only touch the indexes once the map is safely in public.
        os.replace(src, dest)
        write_index_lines(INDEX_FILE, index_upsert(read_index_lines(INDEX_FILE), base, mode, str(size)))
        write_index_lines(PENDING_INDEX_FILE, index_remove(read_index_lines(PENDING_INDEX_FILE), base))
    return True


def reject_map(base):
    """Delete pending/<base>.map and drop it from the review queue. Returns True if
    the map existed, False if there was nothing to reject."""
    src = os.path.join(PENDING_DIR, base + ".map")
    existed = os.path.isfile(src)
    with INDEX_LOCK:
        if existed:
            try:
                os.remove(src)
            except OSError:
                return False
        write_index_lines(PENDING_INDEX_FILE, index_remove(read_index_lines(PENDING_INDEX_FILE), base))
    return existed


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

    def _basic_auth_ok(self):
        """True if the request carries HTTP Basic Auth whose password equals the admin
        token (username ignored). This is how the browser admin panel authenticates -
        the browser prompts once and re-sends the credentials on every request."""
        if not ADMIN_TOKEN:
            return False
        hdr = self.headers.get("Authorization", "")
        if not hdr.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(hdr[6:]).decode("utf-8", "replace")
        except Exception:
            return False
        _, _, password = decoded.partition(":")
        return password == ADMIN_TOKEN

    def _admin_ok(self, params):
        """Gate for moderation: accept EITHER the ?token= query (the in-game client)
        OR HTTP Basic Auth (the browser panel). Both check against the admin token."""
        token = (params.get("token") or [""])[0]
        if bool(ADMIN_TOKEN) and token == ADMIN_TOKEN:
            return True
        return self._basic_auth_ok()

    def _require_basic_auth(self):
        """Send a 401 that makes the browser show its native login dialog."""
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="SimpleFighter map approver"')
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # --- Downloads (public) + admin panel/queue (auth-gated) ---------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        # Let's Encrypt (win-acme) HTTP-01 validation: serve the challenge files it
        # drops in ROOT\.well-known\acme-challenge\. Public, HTTP, no redirect - this
        # is how the cert gets issued and auto-renewed without stopping the server.
        if path.startswith("/.well-known/acme-challenge/"):
            token = path[len("/.well-known/acme-challenge/"):]
            if not re.match(r"^[A-Za-z0-9_-]+$", token):
                return self._reply(404, "Not found")
            return self._serve_file(os.path.join(ROOT, ".well-known", "acme-challenge", token), "text/plain")
        # The admin panel is the site root. It sits behind Basic Auth, so a visitor
        # without the password never even sees it (the browser blocks them at 401).
        if path in ("/", "/index.html"):
            # When HTTPS is configured, the panel is HTTPS-only: bounce an http visit
            # to https so the login is never sent in the clear.
            if getattr(self.server, "https_enabled", False) and not getattr(self.server, "is_tls", False):
                host = self.headers.get("Host", "").split(":")[0]
                self.send_response(301)
                self.send_header("Location", "https://" + host + self.path)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if not self._basic_auth_ok():
                return self._require_basic_auth()
            return self._serve_file(os.path.join(ROOT, "index.html"), "text/html; charset=utf-8")
        # Download list + packs stay PUBLIC (players need them; no auth).
        if path == "/public_index.txt":
            return self._serve_file(INDEX_FILE, "text/plain")
        if path.startswith("/maps/public/"):
            name = safe_map_name(urllib.parse.unquote(path[len("/maps/public/"):]))
            if name is None:
                return self._reply(404, "Not found")
            return self._serve_file(os.path.join(PUBLIC_DIR, name), "application/octet-stream")
        if path == "/admin/pending":
            if not self._admin_ok(urllib.parse.parse_qs(parsed.query)):
                return self._reply(403, "Invalid admin token.")
            return self._reply(200, "\r\n".join(list_pending_maps()))
        # Note: /maps/pending/ is deliberately NOT served - pending uploads are private until approved.
        return self._reply(404, "Not found")

    # --- Admin moderation (approve/reject, admin token required) ------------
    def _admin_action(self, params, action):
        if not self._admin_ok(params):
            return self._reply(403, "Invalid admin token.")
        sname = safe_map_name((params.get("name") or [""])[0])
        if sname is None:
            return self._reply(400, "Invalid map name.")
        base = sname[:-4]
        if action == "approve":
            ok = approve_map(base)
        else:
            ok = reject_map(base)
        if not ok:
            return self._reply(404, "That map is not in the pending queue.")
        return self._reply(200, "OK")

    # --- Uploads (moderated: land in pending, never auto-published) ---------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/admin/approve":
            return self._admin_action(params, "approve")
        if parsed.path == "/admin/reject":
            return self._admin_action(params, "reject")
        if parsed.path != "/upload":
            return self._reply(404, "Not found")
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


def make_server(port, https_enabled, is_tls):
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    srv.daemon_threads = True    # HTTP/1.1 keep-alive holds worker threads open; make them daemon so
    srv.block_on_close = False   # closing the window (or Ctrl+C) kills the process instead of hanging on them
    srv.https_enabled = https_enabled  # whether an HTTPS panel exists (drives the http->https redirect)
    srv.is_tls = is_tls                # whether THIS listener is the TLS one
    return srv


def main():
    set_window_title("SimpleFighter map server")
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(PENDING_DIR, exist_ok=True)

    https_enabled = bool(CERT_FILE) and bool(KEY_FILE) and os.path.isfile(CERT_FILE) and os.path.isfile(KEY_FILE)

    server = make_server(PORT, https_enabled, is_tls=False)
    print("SimpleFighter map server running on port %d." % PORT)
    print("Serving downloads from %s" % PUBLIC_DIR)
    print("Accepting uploads into  %s" % PENDING_DIR)

    if https_enabled:
        https_server = make_server(HTTPS_PORT, https_enabled, is_tls=True)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(CERT_FILE, KEY_FILE)
        https_server.socket = ctx.wrap_socket(https_server.socket, server_side=True)
        threading.Thread(target=https_server.serve_forever, daemon=True).start()
        print("Admin panel available over HTTPS on port %d (http visits redirect to https)." % HTTPS_PORT)
    else:
        print("Admin panel over HTTP only (set CERT_FILE and KEY_FILE to enable HTTPS for it).")

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
