# SimpleFighter map approver.
#
# The moderation half of the map server. Uploaded maps land in maps\pending\
# (and get a line in pending_index.txt) but are NEVER downloadable until you
# approve them here. This tool is what you run to review that queue: it moves an
# approved map into maps\public\ and into public_index.txt (the download list),
# or throws a rejected one away.
#
# It talks to NO network - it just reads and moves files on this machine, so it
# is safe to run while the map server is running. Double-click it (it pauses on
# exit so you can read anything), or run "python sf_map_approver.py".
#
# ---------------------------------------------------------------------------
# EDIT THIS SETTING (must match sf_map_server.py's ROOT):
# ---------------------------------------------------------------------------
ROOT = r"C:\Users\Administrator\Desktop\SimpleFighter"  # the folder holding the index files and the maps folder
# ---------------------------------------------------------------------------

import os
import re

PUBLIC_DIR = os.path.join(ROOT, "maps", "public")                    # live, downloadable maps
PENDING_DIR = os.path.join(ROOT, "maps", "pending")                  # uploads waiting for approval
PUBLIC_INDEX_FILE = os.path.join(ROOT, "maps", "public_index.txt")   # the download list players see
PENDING_INDEX_FILE = os.path.join(ROOT, "maps", "pending_index.txt") # the review queue

# A safe map filename: letters, digits, underscore, dot, dash; ends in .map; no spaces or path parts.
SAFE_NAME = re.compile(r"^[A-Za-z0-9_.\-]+\.map$")


def human_size(n):
    """A friendly size string, e.g. '3.89 KB'. Falls back to bytes on bad input."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "unknown size"
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            if unit == "bytes":
                return "%d bytes" % int(n)
            return "%.2f %s" % (n, unit)
        n /= 1024.0


# --- index file helpers (name|mode|bytes lines, CRLF, matching the server) ---
def load_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f.read().splitlines() if ln.strip()]


def save_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines))


def base_of(line):
    return line.split("|", 1)[0]


def index_lookup(lines):
    """base -> (mode, size) from a list of name|mode|bytes lines."""
    out = {}
    for ln in lines:
        parts = ln.split("|")
        base = parts[0]
        mode = parts[1] if len(parts) > 1 else ""
        size = parts[2] if len(parts) > 2 else ""
        out[base] = (mode, size)
    return out


def remove_base(lines, base):
    return [ln for ln in lines if base_of(ln) != base]


def upsert(lines, base, mode, size):
    kept = [ln for ln in lines if base_of(ln) != base]
    kept.append("%s|%s|%s" % (base, mode, size))
    return kept


# --- the queue --------------------------------------------------------------
def list_pending():
    """Real .map files in pending, enriched with mode/size from pending_index.txt.
    Works off the files on disk (authoritative) so a missing or stale index line
    can't hide a map or block a review. Returns a list of dicts."""
    if not os.path.isdir(PENDING_DIR):
        return []
    idx = index_lookup(load_lines(PENDING_INDEX_FILE))
    maps = []
    for fname in sorted(os.listdir(PENDING_DIR)):
        if not SAFE_NAME.match(fname):
            continue  # skip the index or any stray non-map file
        path = os.path.join(PENDING_DIR, fname)
        if not os.path.isfile(path):
            continue
        base = fname[:-4]
        mode, _ = idx.get(base, ("", ""))
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0
        maps.append({"base": base, "fname": fname, "mode": mode or "unknown", "size": size})
    return maps


def approve(m):
    """Move the map into public and its line into public_index.txt."""
    src = os.path.join(PENDING_DIR, m["fname"])
    dest = os.path.join(PUBLIC_DIR, m["fname"])
    if not os.path.isfile(src):
        print("  That map is no longer in the pending folder; skipping.")
        return
    if os.path.exists(dest):
        ans = input("  A public map named %s already exists. Overwrite it? (y/n): " % m["fname"]).strip().lower()
        if ans != "y":
            print("  Left it alone.")
            return
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    # Move the file first; only touch the indexes once the map is safely in public.
    os.replace(src, dest)
    mode = "" if m["mode"] == "unknown" else m["mode"]
    save_lines(PUBLIC_INDEX_FILE, upsert(load_lines(PUBLIC_INDEX_FILE), m["base"], mode, m["size"]))
    save_lines(PENDING_INDEX_FILE, remove_base(load_lines(PENDING_INDEX_FILE), m["base"]))
    print("  Approved. %s is now downloadable." % m["fname"])


def reject(m):
    """Throw the pending map away and drop it from the review queue."""
    ans = input("  Really reject and delete %s? This can't be undone. (y/n): " % m["fname"]).strip().lower()
    if ans != "y":
        print("  Left it in the queue.")
        return
    src = os.path.join(PENDING_DIR, m["fname"])
    if os.path.isfile(src):
        try:
            os.remove(src)
        except OSError as e:
            print("  Could not delete the file: %r" % e)
            return
    save_lines(PENDING_INDEX_FILE, remove_base(load_lines(PENDING_INDEX_FILE), m["base"]))
    print("  Rejected. %s has been deleted." % m["fname"])


def set_window_title(title):
    """Set the console window title on Windows. Harmless no-op elsewhere."""
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def main():
    set_window_title("SimpleFighter map approver")
    while True:
        maps = list_pending()
        if not maps:
            print("\nNo maps are waiting for approval. The queue is empty.")
            return
        print("\nMaps waiting for approval (%d):" % len(maps))
        for i, m in enumerate(maps, 1):
            print("  %d. %s  -  %s map, %s" % (i, m["base"], m["mode"], human_size(m["size"])))
        choice = input("\nEnter a number to review, or q to quit: ").strip().lower()
        if choice in ("q", "quit", "exit", ""):
            return
        try:
            n = int(choice)
        except ValueError:
            print("Please enter a number or q.")
            continue
        if n < 1 or n > len(maps):
            print("That number isn't in the list.")
            continue
        m = maps[n - 1]
        print("\n%s  -  %s map, %s" % (m["base"], m["mode"], human_size(m["size"])))
        action = input("(a)pprove, (r)eject, or (s)kip: ").strip().lower()
        if action in ("a", "approve"):
            approve(m)
        elif action in ("r", "reject"):
            reject(m)
        else:
            print("  Skipped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping.")
    except Exception as e:
        print("\nApprover error: %r" % e)
    input("\nPress Enter to close this window...")
