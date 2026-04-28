import subprocess
import os
import sys
import shutil
import configparser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(SCRIPT_DIR, "tools.ini"))

_tools = configparser.ConfigParser()
_tools.read(os.path.join(os.path.expanduser("~"), ".game_tools", "tools.ini"))

GAME         = _cfg["game"]["name"]
PASSWORD     = _cfg["game"]["password"]
NVGT_FILE    = _cfg["game"]["nvgt_file"]
NVGT_OUT     = os.path.splitext(NVGT_FILE)[0]

INSTALLER_ISS = _cfg["installer"]["iss"]
APP_ID       = _cfg["installer"]["app_id"]
APP_URL      = _cfg["installer"]["app_url"]
EXE_NAME     = _cfg["installer"]["exe_name"]

SITE_HTML    = _cfg["site"]["html"]
SITE_REPO    = _cfg["site"]["repo"]
SITE_PATH    = _cfg["site"]["path"]

NVGT    = _tools["tools"]["nvgt"]
SEVENZIP = _tools["tools"]["sevenzip"]
ISCC    = _tools["tools"]["iscc"]
GH      = _tools["tools"]["gh"]

WIN_SOURCE   = os.path.join(REPO_DIR, "releases", "windows", f"{GAME}_windows_portable_password_is_{PASSWORD}", NVGT_OUT)
ARCHIVE_DIR  = os.path.join(REPO_DIR, "releases", "archives")
ARCHIVE_NAME = f"{GAME}_windows_portable_password_is_{PASSWORD}.7z"
ARCHIVE      = os.path.join(ARCHIVE_DIR, ARCHIVE_NAME)
INSTALLER    = os.path.join(ARCHIVE_DIR, f"{GAME}_windows_installer_password_is_{PASSWORD}.exe")
RELEASE_DIR  = os.path.join(REPO_DIR, "releases", "windows", f"{GAME}_windows_portable_password_is_{PASSWORD}")

SKIP = 0
DO = 1
SILENT_SKIP = 2

def ask(prompt):
    return input(f"{prompt} (Y/N): ").strip().upper() == "Y"

def run(args, capture=False):
    return subprocess.run(args, cwd=REPO_DIR, capture_output=capture, text=True)

def run_out(args):
    return run(args, capture=True).stdout.strip()

def run_cmd(args, cwd=None):
    return subprocess.run(args, cwd=cwd).returncode == 0

def clip(text):
    subprocess.run("clip", input=text.strip(), text=True)

def get_version():
    with open(os.path.join(SCRIPT_DIR, "version.txt"), "r") as f:
        return f.read().strip()

# ── Commit ────────────────────────────────────────────────────────────────────

def unpushed_count():
    out = run_out(["git", "log", "origin/HEAD..HEAD", "--oneline"])
    return len([l for l in out.splitlines() if l.strip()])

def do_commit():
    status = run_out(["git", "status", "--short"])
    changes = len([l for l in status.splitlines() if l.strip()])
    print(f"Changes: {changes}")
    print()
    if changes == 0:
        print("No changes to commit.")
        return
    print(status)
    print()
    if not ask("Do you want to commit?"):
        print("Cancelled.")
        return
    print()
    summary = input("Commit summary: ").strip()
    if not summary:
        print("Summary cannot be empty.")
        return
    print()
    print("Commit description (enter lines one by one, blank line to finish):")
    desc_lines = []
    while True:
        line = input(f"Line {len(desc_lines) + 1}: ")
        if not line.strip():
            break
        desc_lines.append(line)
    description = "\n".join(desc_lines)
    print()
    print(f"Summary:     {summary}")
    if description:
        print(f"Description: {description}")
    print()
    if not ask("Is this correct?"):
        print("Cancelled.")
        return
    print()
    run(["git", "add", "-A"])
    args = ["git", "commit", "-m", summary]
    if description:
        args += ["-m", description]
    result = run(args)
    if result.returncode != 0:
        print("ERROR: Commit failed.")
        return
    print()
    print(f"Committed {changes} file(s).")
    print()
    if not ask("Do you want to push?"):
        print("Changes committed but not pushed.")
        return
    print()
    result = run(["git", "push"])
    if result.returncode != 0:
        print("ERROR: Push failed.")
    else:
        print("Push complete.")

def do_undo(unpushed):
    if unpushed == 0:
        print("Nothing to undo. All commits have been pushed.")
        return
    last_msg = run_out(["git", "log", "-1", "--format=%s"])
    print(f"Last commit: {last_msg}")
    print()
    if not ask("Undo this commit? Your changes will remain staged."):
        print("Cancelled.")
        return
    result = run(["git", "reset", "--soft", "HEAD~1"])
    if result.returncode != 0:
        print("ERROR: Undo failed.")
    else:
        print("Commit undone. Your changes are still staged.")

def do_history():
    raw = run_out(["git", "log", "-50", "--decorate-refs=refs/tags", "--format=%h~%ar~%s%d"])
    commits = []
    print()
    print("Last 50 commits:")
    print()
    for i, line in enumerate(raw.splitlines(), 1):
        parts = line.split("~", 2)
        if len(parts) < 3:
            continue
        sha, date, msg = parts
        commits.append((sha, msg))
        print(f"  {i}. {sha}  {msg}  (Time: {date})")
    print()
    pick = input("Select a commit number (or 0 to go back): ").strip()
    if pick == "0" or pick == "":
        return
    try:
        index = int(pick) - 1
        if index < 0 or index >= len(commits):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return
    sha, msg = commits[index]
    print()
    print(f"Selected: {sha} {msg}")
    commit_menu(sha, msg)

def commit_menu(sha, msg):
    while True:
        print()
        print("========================")
        print(" Commit Options")
        print("========================")
        print(" 1. Show description")
        print(" 2. Copy SHA")
        print(" 3. Create tag")
        print(" 4. Copy tag")
        print(" 5. Reset to this commit")
        print(" 6. Go back")
        print("========================")
        choice = input("Choose an option: ").strip()
        print()
        if choice == "1":
            show_desc(sha)
        elif choice == "2":
            copy_sha(sha)
        elif choice == "3":
            create_tag(sha)
        elif choice == "4":
            copy_tag(sha)
        elif choice == "5":
            if do_reset(sha):
                return
        elif choice == "6":
            do_history()
            return
        else:
            print("Invalid choice.")

def show_desc(sha):
    desc = run_out(["git", "log", "-1", "--format=%B", sha])
    print(desc if desc else "(No description)")
    print()

def copy_sha(sha):
    full = run_out(["git", "rev-parse", sha])
    clip(full)
    print(f"SHA copied to clipboard: {full}")

def create_tag(sha):
    tag_name = input("Enter tag name: ").strip()
    if not tag_name:
        print("Tag name cannot be empty.")
        return
    result = run(["git", "tag", tag_name, sha])
    if result.returncode != 0:
        print("ERROR: Failed to create tag.")
        return
    print(f'Tag "{tag_name}" created.')
    if ask("Push tag to remote?"):
        run(["git", "push", "origin", tag_name])
        print("Tag pushed.")

def copy_tag(sha):
    tag = run_out(["git", "tag", "--points-at", sha])
    if not tag:
        print("No tag found on this commit.")
    else:
        clip(tag)
        print(f"Tag copied to clipboard: {tag}")

def do_reset(sha):
    print("WARNING: Resetting will move HEAD to this commit.")
    print()
    print(" 1. Soft (keeps changes staged)")
    print(" 2. Hard (discards all changes permanently)")
    print(" 3. Cancel")
    print()
    choice = input("Choose reset type: ").strip()
    if choice == "3" or choice == "":
        print("Cancelled.")
        return False
    if choice == "1":
        flag = "--soft"
    elif choice == "2":
        flag = "--hard"
        print()
        print("WARNING: Hard reset will permanently discard all uncommitted changes.")
    else:
        print("Invalid choice.")
        return False
    print()
    if not ask(f"Reset to {sha}?"):
        print("Cancelled.")
        return False
    result = run(["git", "reset", flag, sha])
    if result.returncode != 0:
        print("ERROR: Reset failed.")
        return False
    print("Reset complete.")
    return True

# ── Release ───────────────────────────────────────────────────────────────────

def do_website_update(version, tag, skip_website):
    do_website = False
    if skip_website == DO:
        do_website = True
    elif skip_website == SKIP:
        do_website = ask("Do you want to update the game's website?")

    if not do_website:
        if skip_website == SKIP:
            print("Skipping website update.\n")
        return

    print("Updating website...")
    ps1 = os.path.join(SCRIPT_DIR, "site_updater.ps1")
    if not run_cmd(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1, "-HtmlFile", SITE_HTML, "-Version", version, "-Tag", tag]):
        print("ERROR: Failed to update website HTML.")
        return
    print("Website updated.\n")

    print("Committing website changes...")
    log = subprocess.run(["git", "log", "--oneline"], cwd=SITE_REPO, capture_output=True, text=True).stdout
    if f"Updated {GAME} to version {version}." in log:
        print("WARNING: Commit already exists. Skipping commit.\n")
        return

    run_cmd(["git", "add", SITE_PATH], cwd=SITE_REPO)
    if not run_cmd(["git", "commit", "-m", f"Updated {GAME} to version {version}."], cwd=SITE_REPO):
        print("ERROR: Failed to commit website changes.")
        return
    if not run_cmd(["git", "push"], cwd=SITE_REPO):
        print("ERROR: Failed to push website changes.")
        return
    print("Website committed and pushed.\n")

def run_release(skip_compile, skip_package, skip_release, skip_website, skip_empty_release):
    version = get_version()
    if not version:
        print("ERROR: Could not read version from version.txt.")
        return

    title = f"{GAME} V{version}"
    tag = f"V{version}0"

    print(f"\nVersion: {version}")
    print(f"Tag:     {tag}")
    print(f"Title:   {title}\n")

    # Compile
    do_compile = False
    if skip_compile == DO:
        do_compile = True
    elif skip_compile == SKIP:
        do_compile = ask("Do you want to compile this project?")

    if do_compile:
        shutil.copy(os.path.join(SCRIPT_DIR, "version.txt"), os.path.join(REPO_DIR, "docks", "version.txt"))
        print("Compiling NVGT source...")
        if not run_cmd([NVGT, "-c", "-Q", os.path.join(REPO_DIR, NVGT_FILE)]):
            print("ERROR: NVGT compilation failed.")
            return
        print("Compilation successful.\n")
        print("Replacing compiled output in release folder...")
        cst_out = os.path.join(REPO_DIR, NVGT_OUT)
        cst_dest = os.path.join(RELEASE_DIR, NVGT_OUT)
        if os.path.exists(cst_dest):
            shutil.rmtree(cst_dest)
        shutil.move(cst_out, cst_dest)
        print("Release folder updated.\n")
    elif skip_compile == SKIP:
        print("Skipping compilation.\n")

    # Package
    do_package = False
    if skip_package == DO:
        do_package = True
    elif skip_package == SKIP:
        do_package = ask("Do you want to package this project?")

    if do_package:
        if not os.path.exists(WIN_SOURCE):
            print("ERROR: cst folder not found in release directory. Please compile the full project first.")
            return
        print("Building Windows portable 7z archive...")
        if os.path.exists(ARCHIVE):
            os.remove(ARCHIVE)
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        if not run_cmd([SEVENZIP, "a", "-t7z", ARCHIVE, WIN_SOURCE, "-mx=9", "-m0=LZMA2", "-md=64m", "-mfb=64", "-ms=on", "-mmt=12", f"-p{PASSWORD}", "-mhe=on"]):
            print("ERROR: 7z archive build failed.")
            return
        print("Archive built successfully.\n")
        print("Building Windows installer...")
        if os.path.exists(INSTALLER):
            os.remove(INSTALLER)
        if not run_cmd([ISCC, "/Q",
                        f"/DMyAppId={APP_ID}",
                        f"/DMyAppName={GAME}",
                        f"/DMyAppURL={APP_URL}",
                        f"/DMyAppExeName={EXE_NAME}",
                        f"/DMyAppPassword={PASSWORD}",
                        f"/DMySourcePath={WIN_SOURCE}",
                        os.path.join(SCRIPT_DIR, INSTALLER_ISS)]):
            print("ERROR: Installer build failed.")
            return
        print("Installer built successfully.\n")
    elif skip_package == SKIP:
        print("Skipping packaging.\n")

    # Release
    do_rel = False
    if skip_release == DO:
        do_rel = True
    elif skip_release == SKIP:
        do_rel = ask("Do you want to release this project?")

    if not do_rel:
        if skip_release == SKIP:
            print("Skipping release.\n")
        do_website_update(version, tag, skip_website)
        return

    assets = []
    if os.path.exists(ARCHIVE):
        assets.append(ARCHIVE)
    if os.path.exists(INSTALLER):
        assets.append(INSTALLER)

    if not assets:
        print("WARNING: No assets found.\n")
        proceed = False
        if skip_empty_release == DO:
            proceed = True
        elif skip_empty_release == SKIP:
            proceed = ask("Do you still want to create an empty release?")
        if not proceed:
            print("Release cancelled.\n")
            return

    print(f"Tagging latest commit as {tag}...")
    run_cmd(["git", "tag", "-f", tag], cwd=REPO_DIR)
    run_cmd(["git", "push", "origin", "-f", tag], cwd=REPO_DIR)

    print("\nDeleting existing release if it exists...")
    subprocess.run([GH, "release", "delete", tag, "--yes"], cwd=REPO_DIR, stderr=subprocess.DEVNULL)

    print(f"\nCreating GitHub release {title} with tag {tag}...\n")
    cmd = [GH, "release", "create", tag] + assets + ["--title", title, "--notes", ""]
    if not run_cmd(cmd, cwd=REPO_DIR):
        print("ERROR: GitHub release creation failed.")
        return

    print("\nRelease complete.\n")

    if not assets:
        print("WARNING: No assets were released. Skipping website update.\n")
        return

    do_website_update(version, tag, skip_website)

# ── Main menu ─────────────────────────────────────────────────────────────────

def menu():
    while True:
        unpushed = unpushed_count()
        print()
        print("========================")
        print(f"  {GAME} Tools")
        print("========================")
        print(" --- Commit ---")
        print(" 1. Make a commit")
        print(f" 2. Undo last commit (unpushed: {unpushed})")
        print(" 3. Show commit history")
        print(" --- Release ---")
        print(" 4. Full release")
        print(" 5. Compile only")
        print(" 6. Package only")
        print(" 7. Release only")
        print(" 8. Website only")
        print(" ---")
        print(" 9. Exit")
        print("========================")
        choice = input("Choose an option: ").strip()
        print()
        if choice == "1":
            do_commit()
        elif choice == "2":
            do_undo(unpushed)
        elif choice == "3":
            do_history()
        elif choice == "4":
            run_release(SKIP, SKIP, SKIP, SKIP, SKIP)
        elif choice == "5":
            run_release(DO, SILENT_SKIP, SILENT_SKIP, SILENT_SKIP, SILENT_SKIP)
        elif choice == "6":
            run_release(SILENT_SKIP, DO, SILENT_SKIP, SILENT_SKIP, SILENT_SKIP)
        elif choice == "7":
            run_release(SILENT_SKIP, SILENT_SKIP, DO, SILENT_SKIP, DO)
        elif choice == "8":
            run_release(SILENT_SKIP, SILENT_SKIP, SILENT_SKIP, DO, SILENT_SKIP)
        elif choice == "9":
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1-9.")

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 5:
        flags = [int(a) for a in args[:5]]
        run_release(*flags)
    else:
        menu()
