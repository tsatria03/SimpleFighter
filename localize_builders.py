import re
import os

base = "C:/Users/tonys/OneDrive/Documents/github/SimpleFighter/includes/builder"

files = {
    "construction/blockage.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("paxx=string_to_number(form.get_text(mx2));", "double paxx=string_to_number(form.get_text(mx2));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("paxy=string_to_number(form.get_text(my2));", "double paxy=string_to_number(form.get_text(my2));"),
        ("txt=form.get_text(bltext);", "string txt=form.get_text(bltext);"),
    ],
    "transitions/el_floor.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("paxx=string_to_number(form.get_text(mx2));", "double paxx=string_to_number(form.get_text(mx2));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("txt=form.get_text(elvftext);", "string txt=form.get_text(elvftext);"),
    ],
    "zones/menu_zone.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("paxx=string_to_number(form.get_text(mx2));", "double paxx=string_to_number(form.get_text(mx2));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("paxy=string_to_number(form.get_text(my2));", "double paxy=string_to_number(form.get_text(my2));"),
    ],
    "misc/spawnpoint.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
    ],
    "interaction/text square.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("txt=form.get_text(tqtext);", "string txt=form.get_text(tqtext);"),
    ],
    "misc/timedtext.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("paxx=string_to_number(form.get_text(mx2));", "double paxx=string_to_number(form.get_text(mx2));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("paxy=string_to_number(form.get_text(my2));", "double paxy=string_to_number(form.get_text(my2));"),
        ("speedtime=string_to_number(form.get_text(sp));", "double speedtime=string_to_number(form.get_text(sp));"),
        ("txt=form.get_text(tmtext);", "string txt=form.get_text(tmtext);"),
    ],
    "misc/travelpoint.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("paxx=string_to_number(form.get_text(mx2));", "double paxx=string_to_number(form.get_text(mx2));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("paxy=string_to_number(form.get_text(my2));", "double paxy=string_to_number(form.get_text(my2));"),
        ("txt=form.get_text(dmap);", "string txt=form.get_text(dmap);"),
        ("x2=string_to_number(form.get_text(dx));", "double x2=string_to_number(form.get_text(dx));"),
        ("y2=string_to_number(form.get_text(dy));", "double y2=string_to_number(form.get_text(dy));"),
        ("txt2=form.get_text(dtext);", "string txt2=form.get_text(dtext);"),
    ],
    "zones/zone.nvgt": [
        ("x=string_to_number(form.get_text(mx));", "double x=string_to_number(form.get_text(mx));"),
        ("paxx=string_to_number(form.get_text(mx2));", "double paxx=string_to_number(form.get_text(mx2));"),
        ("y=string_to_number(form.get_text(my));", "double y=string_to_number(form.get_text(my));"),
        ("paxy=string_to_number(form.get_text(my2));", "double paxy=string_to_number(form.get_text(my2));"),
        ("txt=form.get_text(zntext);", "string txt=form.get_text(zntext);"),
    ],
}

for filepath, replacements in files.items():
    full_path = os.path.join(base, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)
            print(f"  Replaced in {filepath}: {old[:40]}...")
        else:
            print(f"  WARNING: Not found in {filepath}: {old[:40]}...")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Done: {filepath}")

print("\nAll done!")
