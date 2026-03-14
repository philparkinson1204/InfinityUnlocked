# Disney Infinity 1.0 — Character Freedom Mod

**Play any character in any playset.** Sorcerer Mickey in Incredibles, Jack Sparrow in Monsters University, Elsa in Pirates — endless possibility.

This has never been achieved in the game's 13-year history.

## What It Does

Disney Infinity 1.0 restricts each character to their "home" playset — Mr. Incredible can only play in the Incredibles world, Sully only in Monsters University, etc. This mod removes that restriction entirely through:

1. **17 binary patches to the exe** — NOPs all conditional jumps after `FindPlaysetForCharacter` calls across 6 code areas (System_IsCharacterValid, NFC enforcement, avatar management, character management, zone management, playset management)
2. **3 modified data zip files** — Expands actor lists, bitmask filters, PlayableAvatars fields, and unlocks all customization items

No DLL injection. No runtime memory hacking. Pure static binary + data patches.

## Requirements

- Disney Infinity 1.0: Gold Edition (Steam)
- Python 3.6+ (for the exe patcher)
- An **unmodified** `DisneyInfinity1.exe` matching this hash:

| Property | Value |
|---|---|
| SHA256 | `22C596D4AF825981CA9F5D845FB7068197B544B9C4F12A9954C2D39EFF502AC0` |
| File size | 20,648,448 bytes (19.7 MB) |

## Installation

### Step 1: Back up your game

Copy your entire game folder or at minimum these files:
```
<game>/DisneyInfinity1.exe
<game>/assets/gamedb/core/core.zip
<game>/assets/startup2.zip
<game>/assets/gamedb/gamedb.zip
```

Your game folder is typically:
```
C:\Program Files (x86)\Steam\steamapps\common\Disney Infinity Gold Edition\
```

### Step 2: Patch the exe

```
python patch_exe.py "<game>/DisneyInfinity1.exe"
```

The patcher will verify the file hash, create a backup, and apply all 17 patches.

### Step 3: Install the data files

Copy the three modified zip files into your game directory, replacing the originals:

| Modified file | Copy to |
|---|---|
| `data_patches/core.zip` | `<game>/assets/gamedb/core/core.zip` |
| `data_patches/startup2.zip` | `<game>/assets/startup2.zip` |
| `data_patches/gamedb.zip` | `<game>/assets/gamedb/gamedb.zip` |

### Step 4: Launch and play

1. Launch Disney Infinity 1.0 from Steam
2. Place any character on the virtual base
3. Select any playset — all characters will be available

## Save File Notes

- **Existing saves work fine.** You do not need to start fresh.
- If characters appear greyed out in the picker, it may be due to `MigratedLocks=1` in an old save. In that case, delete your save folder and let the game create a new one:
  ```
  <Steam>/userdata/<your_steam_id>/237450/remote/Disney Infinity 1.0/
  ```
- The mod unlocks all 96 customization items (IGP entries set from LOCKED to AVAILABLE), so everything should be accessible immediately.

## What's Modified (Technical Detail)

### EXE: 17 Binary Patches

All patches NOP (`0x90`) conditional jumps that follow calls to `GameManager::FindPlaysetForCharacter` (VA `0x0048CB50`). This function is called 13 times across the codebase to enforce playset restrictions.

| Group | Code Area | Patches | Description |
|---|---|---|---|
| 1 | System_IsCharacterValid | 2 | Lua-callable gate function |
| 2 | NFC Enforcement | 3 | Physical figure placement validation |
| 3 | Avatar Management | 6 | Character loading and swapping |
| 4 | Character Management | 1 | Character selection validation |
| 5 | Zone Management | 3 | Zone transition checks |
| 6 | Playset Management | 2 | Playset entry validation |

See `patch_exe.py` for exact offsets and byte values.

### Data: 3 Modified Zip Files

**core.zip** — Actor lists (Layer 1)
All 6 playset actor files expanded to include all 40 characters using the Toy Box master list (`rumpusroom_actors.lua`) as template. This ensures character assets are loaded in every playset.
- `cars_actors.lua`, `incredibles_actors.lua`, `loneranger_actors.lua`
- `monstersu_actors.lua`, `pirates_actors.lua`, `toystoryinspace_actors.lua`

**startup2.zip** — Bitmask filters + PlayableAvatars (Layers 2 & 3)
- `bitmasks.lua`: All `AV_Avatar*` groups expanded to include all characters
- `zonelist_dec.lua`: All 8 playset zone `PlayableAvatars` fields set to the full 40-character list

**gamedb.zip** — Customization unlocks (Layer 4)
- `customizationclouddata.lua`: All 96 IGP entries changed from `State="LOCKED"` to `State="AVAILABLE"`

## Uninstalling

1. Replace the patched exe with the backup created by the patcher (`DisneyInfinity1_BACKUP.exe`)
2. Restore the three original zip files from your backup, or verify game files through Steam (Properties > Local Files > Verify integrity of game files)

## How It Was Discovered

The restriction wasn't in one place — it was enforced at **6 different layers of C++ code** with **13 separate validation call sites**. Patching just the Lua gate (`System_IsCharacterValid`) was not enough because native C++ code also checks during NFC figure placement, avatar loading, zone transitions, and playset management.

Approaches that failed: DLL proxy injection (thread-unsafe Lua crashes), single-point patching, FindPlaysetForCharacter return value manipulation, CreateRemoteThread, DirectX EndScene hooks, and data-file-only modifications (C++ validation still blocks).

The solution was to NOP every conditional jump after every call to `FindPlaysetForCharacter` in the entire binary, combined with data file modifications to ensure character assets are loaded everywhere.

## Credits

Created by **Philip Parkinson II**.

Reverse engineering and binary analysis performed with [Claude Code](https://claude.ai/claude-code) by Anthropic.
Model: Opus 4.6 (high reasoning)
