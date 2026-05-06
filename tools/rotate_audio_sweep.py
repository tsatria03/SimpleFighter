"""
Dry-run sweep that rewrites play_3d / play_extended_3d / update_listener_3d
calls so the listener rotation arg picks up me_rotation when the listener is
the player.

Strategy:
- Find every call to one of the three functions.
- Parse args by splitting on top-level commas (parens-balanced).
- For play_3d / play_extended_3d: if args[1..3] == ['me.x','me.y','me.z']
  and args[7] is the literal '0', rewrite args[7] to 'calculate_theta(me_rotation)'.
- For update_listener_3d: if args[0..2] == ['me.x','me.y','me.z']
  and args[3] is missing or '0', rewrite/add a rotation arg of
  'calculate_theta(me_rotation)'.

Default mode: dry run. Prints planned diffs to stdout, writes nothing.
Pass --apply to actually write the files.
"""

import os
import re
import sys

ROOT = r"C:\Users\tonys\OneDrive\Documents\github\SimpleFighter\includes"
SKIP = {os.path.normpath(os.path.join(ROOT, "main", "deps", "sound_pool.nvgt")),
        os.path.normpath(os.path.join(ROOT, "main", "deps", "rotation.nvgt")),
        os.path.normpath(os.path.join(ROOT, "main", "globals", "decpool.nvgt"))}

# Match a call's opening: function name followed by '('.
CALL_RE = re.compile(r"\b(play_3d|play_extended_3d|update_listener_3d)\s*\(")

LISTENER = ("me.x", "me.y", "me.z")
NEW_ROT = "calculate_theta(me_rotation)"


def find_matching_paren(s, start):
    """Given s[start] == '(', return index of matching ')' (inclusive)."""
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def split_top_level_args(arglist):
    """Split 'a, b(c,d), e' into ['a','b(c,d)','e'] honoring parens/quotes."""
    args = []
    depth = 0
    in_str = False
    str_ch = ""
    cur = []
    for c in arglist:
        if in_str:
            cur.append(c)
            if c == str_ch and (len(cur) < 2 or cur[-2] != '\\'):
                in_str = False
            continue
        if c in ('"', "'"):
            in_str = True
            str_ch = c
            cur.append(c)
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if c == ',' and depth == 0:
            args.append(''.join(cur))
            cur = []
        else:
            cur.append(c)
    if cur:
        args.append(''.join(cur))
    return args


def normalize(arg):
    return arg.strip().replace(' ', '')


def rewrite_call(func, arglist):
    """Return the rewritten arglist or None if no change."""
    args = split_top_level_args(arglist)
    if func in ("play_3d", "play_extended_3d"):
        # args: [filename, lx, ly, lz, sx, sy, sz, rotation, ...]
        if len(args) < 8:
            return None
        listener = tuple(normalize(a) for a in args[1:4])
        if listener != LISTENER:
            return None
        if normalize(args[7]) != "0":
            return None
        # Preserve original whitespace prefix on the rotation arg.
        orig = args[7]
        prefix_ws = orig[:len(orig) - len(orig.lstrip())]
        suffix_ws = orig[len(orig.rstrip()):]
        args[7] = f"{prefix_ws}{NEW_ROT}{suffix_ws}"
        return ','.join(args)
    if func == "update_listener_3d":
        # args: [lx, ly, lz, rotation?]
        if len(args) < 3:
            return None
        listener = tuple(normalize(a) for a in args[0:3])
        if listener != LISTENER:
            return None
        if len(args) == 3:
            args.append(f" {NEW_ROT}")
            return ','.join(args)
        if normalize(args[3]) == "0":
            orig = args[3]
            prefix_ws = orig[:len(orig) - len(orig.lstrip())]
            suffix_ws = orig[len(orig.rstrip()):]
            args[3] = f"{prefix_ws}{NEW_ROT}{suffix_ws}"
            return ','.join(args)
        return None
    return None


def process_text(text):
    """Return (new_text, list_of_(line_no, before, after)) for changes."""
    out = []
    changes = []
    i = 0
    while i < len(text):
        m = CALL_RE.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        func = m.group(1)
        open_paren = m.end() - 1
        close_paren = find_matching_paren(text, open_paren)
        if close_paren == -1:
            out.append(text[m.start():])
            break
        arglist = text[open_paren + 1:close_paren]
        new_arglist = rewrite_call(func, arglist)
        if new_arglist is not None and new_arglist != arglist:
            line_no = text[:m.start()].count('\n') + 1
            before = text[m.start():close_paren + 1]
            after = f"{func}({new_arglist})"
            changes.append((line_no, before, after))
            out.append(after)
        else:
            out.append(text[m.start():close_paren + 1])
        i = close_paren + 1
    return ''.join(out), changes


def main():
    apply = "--apply" in sys.argv
    total_changes = 0
    for dirpath, _, filenames in os.walk(ROOT):
        for fn in filenames:
            if not fn.endswith(".nvgt"):
                continue
            path = os.path.normpath(os.path.join(dirpath, fn))
            if path in SKIP:
                continue
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            new_src, changes = process_text(src)
            if changes:
                rel = os.path.relpath(path, ROOT)
                print(f"\n=== {rel} ({len(changes)} change{'s' if len(changes) != 1 else ''}) ===")
                for line_no, before, after in changes:
                    print(f"  L{line_no}:")
                    print(f"    - {before}")
                    print(f"    + {after}")
                total_changes += len(changes)
                if apply and new_src != src:
                    with open(path, "w", encoding="utf-8", newline="") as fh:
                        fh.write(new_src)
    print(f"\nTotal: {total_changes} call(s) {'rewritten' if apply else 'would be rewritten'}.")
    if not apply:
        print("Re-run with --apply to write the changes.")


if __name__ == "__main__":
    main()
