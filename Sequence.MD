# MPC 1000 `.SEQ` File Format (JJOS 4.50)

Researched from `00_TEST.SEQ` and validated against 28 additional `.SEQ` files.

## Overall Layout

| Offset | Size | Contents |
|--------|------|----------|
| `0x0000` | 48 bytes | Header |
| `0x0030` | 3840 bytes | Bar map table (1000 × 4-byte entries) |
| `0x0FD0` | 3120 bytes | Track section (65 tracks × 48 bytes each) |
| `0x1C00` | 768 bytes | MIDI event data |

---

## Header (48 bytes)

| Offset | Size | Value (example) | Meaning |
|--------|------|-----------------|---------|
| `0x00` | 4 | `d0 1e 00 00` | File size, LE uint32 |
| `0x04` | 17 | `MPC1000 SEQ 4.50\0` | Magic string + null terminator |
| `0x15` | 1 | `0x02` | Sequence length in bars |
| `0x1A` | 2 | `0x03E8` | Tempo × 10, LE uint16 (1000 → 100.0 BPM) |
| `0x20` | 4 | `0x04B0` | File offset pointer into bar map table |

---

## Bar Map Table (`0x0030`–`0x0FCF`)

1000 × 4-byte entries. Each entry maps bar number N to its starting tick position.

| Bytes | Contents |
|-------|----------|
| `[0:3]` | Tick position, 3-byte little-endian uint24. Always `N × 384`. |
| `[3]` | `0x60` = 96 = PPQ constant |

The MPC 1000 uses **96 PPQ**. In 4/4 time, one bar = 96 × 4 = **384 ticks**. This table precomputes bar start positions for up to 999 bars.

---

## Track Section (`0x0FD0`–`0x1BFF`)

65 tracks (Track00–Track64), each **48 bytes**:

| Bytes | Contents |
|-------|----------|
| `[0:16]` | Track name, null-padded ASCII (16 bytes) |
| `[16]` | `0x00` separator byte |
| `[17:32]` | Program name, null-padded ASCII (15 bytes) |
| `[34]` | MIDI channel (`0xFF` = unassigned) |
| `[36]` | Velocity (`0x64` = 100, the default) |
| `[47]` | `0x32` record terminator (always present) |

### Program Name Field (`[17:32]`)

This is the filename of the `.PGM` program file referenced by the track, without the `.PGM` extension. Three sentinel values indicate no file reference:

- `"1KOSC"` — track uses the MPC's internal oscillator
- `"OFF"` — no program assigned
- `"unused"` — track slot cleared (seen in some files alongside the above)

A track slot may also be entirely zeroed (all null bytes), meaning unused.

### Extracting Program References

To find all `.PGM` files referenced by a sequence:

1. Seek to `0x0FD0` — use this **fixed offset**, do not search for `"Track00"` (that slot may be zeroed)
2. Iterate 65 × 48-byte blocks
3. For each block, read bytes `[17:32]`, strip null bytes
4. Skip sentinels: `"1KOSC"`, `"OFF"`, `"unused"`, and empty strings
5. Append `.PGM` to the remaining names

### Example (from `00_TEST.SEQ`)

| Track index | Track name | Program file | MIDI channel |
|-------------|-----------|--------------|--------------|
| 02 | `MPC_AJWR` | `AJ_WARBLE.PGM` | 6 |
| 06 | `1_BEEPS` | `BEEPS.PGM` | 10 |
| 10 | `2_AHH` | `CAPS_AHH.PGM` | 20 |

---

## MIDI Event Data (`0x1C00`–`0x1ECF`)

Begins with a 16-byte separator:
```
FF FF FF FF FF 00 FF FF FF FF FF FF FF FF FF FF
```

Followed by N × **16-byte event records**:

| Bytes | Contents |
|-------|----------|
| `[0:4]` | Tick position, LE uint32 |
| `[4]` | MIDI channel (0–15) |
| `[5]` | MIDI command (`0x90` = Note On) |
| `[6]` | Note number (0–127) |
| `[7]` | Velocity (0–127) |
| `[8:12]` | Duration in ticks, LE uint32 |
| `[12:16]` | Zero padding |

Terminated by a 16-byte end marker:
```
FF FF FF 7F FF FF FF FF FF FF FF FF FF FF FF FF
```

All events across all tracks are stored in a single flat list, sorted by tick position. The MIDI channel in each event corresponds to the channel assigned to a track in the track section.
