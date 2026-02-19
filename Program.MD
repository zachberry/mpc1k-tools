# MPC 1000 `.PGM` File Format (JJOS 8.00)

Researched from 109 PGM files. All files are identical in size and version.

## Overall Layout

| Offset | Size | Contents |
|--------|------|----------|
| `0x0000` | 24 bytes | Header |
| `0x0018` | 10496 bytes | Pad blocks (64 × 164 bytes) |
| `0x2918` | 236 bytes | Footer (character table + program settings) |

**Total file size: always 10756 bytes (`0x2A04`)**

---

## Header (24 bytes)

| Offset | Size | Value | Meaning |
|--------|------|-------|---------|
| `0x00` | 4 | `04 2a 00 00` | File size, LE uint32 (always 10756) |
| `0x04` | 17 | `MPC1000 PGM 8.00\0` | Magic string + null terminator |
| `0x15` | 1 | `0x00` | Unknown |
| `0x16` | 1 | `0x08` | Unknown (consistent across all files) |
| `0x17` | 1 | `0x01` | Unknown |

---

## Pad Blocks (`0x0018`–`0x2917`)

**64 pad slots**, each **164 bytes** (`0xA4`). Pads are numbered 0–63, corresponding to the MPC's A01–D16 pad layout (4 banks × 16 pads).

### Pad Block Structure (164 bytes)

| Bytes | Contents |
|-------|----------|
| `[0:16]` | Sample name, null-padded ASCII (16 bytes) |
| `[16]` | `0x00` separator |
| `[17]` | Level / volume (0–127; `0x64` = 100 = default) |
| `[18]` | `0x00` |
| `[19]` | `0x7F` = 127 (velocity ceiling or similar) |
| `[20:164]` | Pad settings: tuning, envelope, effects, MIDI, etc. (not fully decoded) |

### Sample Name Field (`[0:16]`)

The sample name is the **WAV filename without the `.WAV` extension**, stored as a null-padded ASCII string up to 16 characters.

- Empty pad slots have all zero bytes in this field.
- The WAV file on the CF card is `<sample_name>.WAV` (case-insensitive on FAT).

### Extracting WAV References from a PGM

1. Seek to `0x0018`
2. Iterate 64 × 164-byte blocks
3. For each block, read bytes `[0:16]`, strip null bytes
4. Any non-empty result is a WAV filename — append `.WAV`

### Example (from `WHO_DRUMS.PGM`)

| Pad | Offset | Sample name | WAV file |
|-----|--------|-------------|----------|
| 00 | `0x0018` | `DRM-sd-airy` | `DRM-sd-airy.WAV` |
| 01 | `0x00BC` | `DRM-cp-echo` | `DRM-cp-echo.WAV` |
| 02 | `0x0160` | `DRM-ch-crispy` | `DRM-ch-crispy.WAV` |
| 03 | `0x0204` | `DRM-sd-dx-mouse` | `DRM-sd-dx-mouse.WAV` |
| 04 | `0x02A8` | `DRM-sd-1-fm-flan` | `DRM-sd-1-fm-flan.WAV` |
| 05 | `0x034C` | `DRM-sd-2-fm-flan` | `DRM-sd-2-fm-flan.WAV` |
| 06–63 | … | (empty) | — |

### Example (from `AJ_WARBLE.PGM`)

| Pad | Sample name | WAV file |
|-----|-------------|----------|
| 00 | `S2AJ_20` | `S2AJ_20.WAV` |
| 01–63 | (empty) | — |

Programs may assign the same sample to multiple pads (e.g., pitched across the keyboard), or one sample per pad (drum style).

---

## Footer (`0x2918`–`0x2A03`)

The footer is fixed content shared across all files:

| Offset | Size | Contents |
|--------|------|----------|
| `0x2918` | ~192 bytes | ASCII character lookup/conversion table |
| `0x29D8` | 44 bytes | Program-level settings (partially repeated block) |

The footer does not contain sample or WAV file references.

---

## Notes

- **152 of 159** unique sample names across all 109 example PGMs match WAV files in the same directory. The 7 exceptions (`FRAME2`, `TAO2`, `TAO4`, etc.) are simply WAV files not included in this sample set — the naming convention is consistent.
- PGM files do **not** embed WAV audio — they only reference samples by name. The WAV files must exist separately on the CF card.
- Both drum-style (one sample per pad) and keygroup-style (same sample on multiple pads across note range) programs use identical structure.
