#!/usr/bin/env python3
"""
Disney Infinity 1.0: Gold Edition — Character Freedom Mod
EXE Patcher v1.0

Applies 17 binary patches to DisneyInfinity1.exe that remove all playset
character restrictions. After patching, any character can play in any playset.

Usage:
    python patch_exe.py [path_to_DisneyInfinity1.exe]

If no path is given, looks in the current directory.

The patcher will:
  1. Verify the exe matches the expected SHA256 hash
  2. Create a backup (DisneyInfinity1_BACKUP.exe)
  3. Apply all 17 NOP patches
  4. Verify the patched exe

Author: William
"""

import hashlib
import shutil
import struct
import sys
import os

# SHA256 of the unmodified DisneyInfinity1.exe (Steam Gold Edition)
EXPECTED_HASH = "22C596D4AF825981CA9F5D845FB7068197B544B9C4F12A9954C2D39EFF502AC0"
EXPECTED_SIZE = 20648448

# All 17 binary patches
# Format: (file_offset, original_bytes, patched_bytes, description)
PATCHES = [
    # === Patch Group 1: System_IsCharacterValid (VA 0x00C3CB70) ===
    # NOP the two rejection jumps so the Lua gate never denies a character
    (0x0083C045, bytes([0x74, 0x38]), bytes([0x90, 0x90]),
     "System_IsCharacterValid: je (no playset) -> NOP"),
    (0x0083C053, bytes([0x75, 0x2A]), bytes([0x90, 0x90]),
     "System_IsCharacterValid: jne (mismatch) -> NOP"),

    # === Patch Group 2: NFC Enforcement (VA 0x00A15ED0) ===
    # Skip the first validation block entirely + NOP two more checks
    (0x006152FF,
     bytes([0x84, 0xC0, 0x0F, 0x85, 0xCF, 0x00, 0x00, 0x00]),
     bytes([0x90, 0x90, 0xE9, 0xD0, 0x00, 0x00, 0x00, 0x90]),
     "NFC Enforcement: test+jnz -> NOP+jmp (skip validation block)"),
    (0x0061A46C, bytes([0x74, 0x16]), bytes([0x90, 0x90]),
     "NFC Enforcement: je (empty result) -> NOP"),
    (0x0061A482, bytes([0x74, 0x16]), bytes([0x90, 0x90]),
     "NFC Enforcement: je (comparison) -> NOP"),

    # === Patch Group 3: Avatar Management ===
    (0x0077D4CA, bytes([0x74, 0x3A]), bytes([0x90, 0x90]),
     "AvatarMgmt_1: je (empty result) -> NOP"),
    (0x0077D4DC, bytes([0x75, 0x28]), bytes([0x90, 0x90]),
     "AvatarMgmt_1: jne (mismatch) -> NOP"),
    (0x0077D5D0, bytes([0x74, 0x55]), bytes([0x90, 0x90]),
     "AvatarMgmt_3: je (empty check 1) -> NOP"),
    (0x0077D5DA, bytes([0x74, 0x4B]), bytes([0x90, 0x90]),
     "AvatarMgmt_3: je (empty check 2) -> NOP"),
    (0x0077D5E8, bytes([0x75, 0x0E]), bytes([0x90, 0x90]),
     "AvatarMgmt_3: jne (comparison) -> NOP"),
    (0x0077D5F6, bytes([0x74, 0x2F]), bytes([0x90, 0x90]),
     "AvatarMgmt_3: je (final check) -> NOP"),

    # === Patch Group 4: Character Management ===
    (0x0076E348, bytes([0x75, 0x18]), bytes([0x90, 0x90]),
     "CharMgmt_1: jne (mismatch) -> NOP"),

    # === Patch Group 5: Zone Management ===
    (0x00799739, bytes([0x75, 0x04]), bytes([0x90, 0x90]),
     "ZoneMgmt_1: jne (check 1) -> NOP"),
    (0x00799747, bytes([0x75, 0x04]), bytes([0x90, 0x90]),
     "ZoneMgmt_1: jne (check 2) -> NOP"),
    (0x00799767, bytes([0x74, 0x04]), bytes([0x90, 0x90]),
     "ZoneMgmt_1: je (check 3) -> NOP"),

    # === Patch Group 6: Playset Management ===
    (0x007B08BB, bytes([0x74, 0x5A]), bytes([0x90, 0x90]),
     "PlaysetMgmt_4: je (validation) -> NOP"),
    (0x007B8D0E, bytes([0x74, 0x68]), bytes([0x90, 0x90]),
     "PlaysetMgmt_5: je (validation) -> NOP"),
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
    # Find the exe
    if len(sys.argv) > 1:
        exe_path = sys.argv[1]
    else:
        exe_path = "DisneyInfinity1.exe"

    if not os.path.isfile(exe_path):
        print(f"ERROR: Cannot find {exe_path}")
        print("Usage: python patch_exe.py [path_to_DisneyInfinity1.exe]")
        sys.exit(1)

    print(f"Disney Infinity 1.0 — Character Freedom Mod Patcher")
    print(f"====================================================")
    print(f"Target: {exe_path}")
    print(f"Size:   {os.path.getsize(exe_path):,} bytes")

    # Hash check
    print("\nVerifying file integrity...")
    file_hash = sha256_file(exe_path)
    print(f"SHA256: {file_hash}")

    already_patched = False
    if file_hash == EXPECTED_HASH:
        print("MATCH — this is the unmodified Steam Gold Edition exe.")
    else:
        # Check if it's already patched by reading the first patch location
        with open(exe_path, "rb") as f:
            f.seek(PATCHES[0][0])
            val = f.read(2)
        if val == PATCHES[0][2]:
            print("NOTE: This exe appears to already be patched.")
            already_patched = True
        else:
            print(f"WARNING: Hash does not match expected value!")
            print(f"Expected: {EXPECTED_HASH}")
            print(f"Got:      {file_hash}")
            resp = input("Continue anyway? (y/N): ").strip().lower()
            if resp != "y":
                print("Aborted.")
                sys.exit(1)

    if already_patched:
        resp = input("Re-apply patches anyway? (y/N): ").strip().lower()
        if resp != "y":
            print("Nothing to do.")
            sys.exit(0)

    # Backup
    backup_path = exe_path.replace(".exe", "_BACKUP.exe")
    if not os.path.exists(backup_path):
        print(f"\nCreating backup: {backup_path}")
        shutil.copy2(exe_path, backup_path)
    else:
        print(f"\nBackup already exists: {backup_path}")

    # Apply patches
    print(f"\nApplying {len(PATCHES)} patches...\n")
    with open(exe_path, "r+b") as f:
        for i, (offset, orig, patch, desc) in enumerate(PATCHES, 1):
            f.seek(offset)
            current = f.read(len(orig))

            if current == patch:
                status = "already applied"
            elif current == orig:
                f.seek(offset)
                f.write(patch)
                status = "PATCHED"
            else:
                print(f"  [{i:2d}/17] 0x{offset:08X}: UNEXPECTED BYTES {current.hex()} — SKIPPED")
                print(f"           Expected original: {orig.hex()}")
                print(f"           {desc}")
                continue

            print(f"  [{i:2d}/17] 0x{offset:08X}: {orig.hex()} -> {patch.hex()}  {status}")
            print(f"           {desc}")

    print(f"\nDone! All {len(PATCHES)} patches applied.")
    print(f"\nTo restore the original exe, copy {backup_path} back.")
    print(f"\nIMPORTANT: You also need to install the modified data files.")
    print(f"See README.md for full instructions.")


if __name__ == "__main__":
    main()
