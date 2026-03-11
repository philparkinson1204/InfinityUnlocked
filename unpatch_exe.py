#!/usr/bin/env python3
"""
Disney Infinity 1.0: Character Freedom Mod — Uninstaller
Reverses all 17 binary patches, restoring the original exe behavior.

Usage:
    python unpatch_exe.py [path_to_DisneyInfinity1.exe]
"""

import hashlib
import sys
import os

EXPECTED_HASH = "22C596D4AF825981CA9F5D845FB7068197B544B9C4F12A9954C2D39EFF502AC0"

PATCHES = [
    (0x0083C045, bytes([0x90, 0x90]), bytes([0x74, 0x38])),
    (0x0083C053, bytes([0x90, 0x90]), bytes([0x75, 0x2A])),
    (0x006152FF,
     bytes([0x90, 0x90, 0xE9, 0xD0, 0x00, 0x00, 0x00, 0x90]),
     bytes([0x84, 0xC0, 0x0F, 0x85, 0xCF, 0x00, 0x00, 0x00])),
    (0x0061A46C, bytes([0x90, 0x90]), bytes([0x74, 0x16])),
    (0x0061A482, bytes([0x90, 0x90]), bytes([0x74, 0x16])),
    (0x0077D4CA, bytes([0x90, 0x90]), bytes([0x74, 0x3A])),
    (0x0077D4DC, bytes([0x90, 0x90]), bytes([0x75, 0x28])),
    (0x0077D5D0, bytes([0x90, 0x90]), bytes([0x74, 0x55])),
    (0x0077D5DA, bytes([0x90, 0x90]), bytes([0x74, 0x4B])),
    (0x0077D5E8, bytes([0x90, 0x90]), bytes([0x75, 0x0E])),
    (0x0077D5F6, bytes([0x90, 0x90]), bytes([0x74, 0x2F])),
    (0x0076E348, bytes([0x90, 0x90]), bytes([0x75, 0x18])),
    (0x00799739, bytes([0x90, 0x90]), bytes([0x75, 0x04])),
    (0x00799747, bytes([0x90, 0x90]), bytes([0x75, 0x04])),
    (0x00799767, bytes([0x90, 0x90]), bytes([0x74, 0x04])),
    (0x007B08BB, bytes([0x90, 0x90]), bytes([0x74, 0x5A])),
    (0x007B8D0E, bytes([0x90, 0x90]), bytes([0x74, 0x68])),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().upper()


def main():
    exe_path = sys.argv[1] if len(sys.argv) > 1 else "DisneyInfinity1.exe"

    if not os.path.isfile(exe_path):
        print(f"ERROR: Cannot find {exe_path}")
        sys.exit(1)

    print(f"Restoring original exe: {exe_path}")

    file_hash = sha256_file(exe_path)
    if file_hash == EXPECTED_HASH:
        print("This exe is already unmodified. Nothing to do.")
        sys.exit(0)

    restored = 0
    with open(exe_path, "r+b") as f:
        for offset, patched, original in PATCHES:
            f.seek(offset)
            current = f.read(len(patched))
            if current == patched:
                f.seek(offset)
                f.write(original)
                restored += 1
            elif current == original:
                pass  # already original
            else:
                print(f"  WARNING: Unexpected bytes at 0x{offset:08X}: {current.hex()}")

    print(f"Restored {restored} patches.")

    file_hash = sha256_file(exe_path)
    if file_hash == EXPECTED_HASH:
        print("Verified: exe matches original hash.")
    else:
        print(f"WARNING: Hash after restore does not match original.")
        print(f"You may want to restore from your backup or verify via Steam.")

    print("\nRemember to also restore the original data zip files")
    print("(or use Steam's 'Verify integrity of game files').")


if __name__ == "__main__":
    main()
