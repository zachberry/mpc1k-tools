"""
MPC 1000 (JJOS) file parser.
See Sequence.MD and Program.MD for format details.

Example usage:
python3 mpc1k.py example/             # scans all SEQ files, reports per-sequence + combined WAV list
python3 mpc1k.py example/00_TEST.SEQ  # single file as before

"""

import os


SEQ_TRACK_OFFSET = 0x0FD0
SEQ_TRACK_SIZE = 48
SEQ_TRACK_COUNT = 65
SEQ_PROG_SENTINELS = {"1KOSC", "OFF", "unused"}

PGM_PAD_OFFSET = 0x0018
PGM_PAD_SIZE = 164
PGM_PAD_COUNT = 64


def parse_seq(seq_path: str) -> list[str]:
    """
    Parse a SEQ file and return the list of PGM filenames it references.
    Filenames are returned as bare names (e.g. 'AJ_WARBLE.PGM'),
    not full paths.
    """
    with open(seq_path, "rb") as f:
        data = f.read()

    if b"MPC1000 SEQ" not in data[4:20]:
        raise ValueError(f"Not a valid MPC1000 SEQ file: {seq_path}")

    pgms = []
    for i in range(SEQ_TRACK_COUNT):
        offset = SEQ_TRACK_OFFSET + i * SEQ_TRACK_SIZE
        block = data[offset : offset + SEQ_TRACK_SIZE]
        prog_name = block[17:32].rstrip(b"\x00").decode("ascii", errors="replace")
        if prog_name and prog_name not in SEQ_PROG_SENTINELS:
            pgm = prog_name + ".PGM"
            if pgm not in pgms:
                pgms.append(pgm)

    return pgms


def parse_pgm(pgm_path: str) -> list[str]:
    """
    Parse a PGM file and return the list of WAV filenames it references.
    Filenames are returned as bare names (e.g. 'S2AJ_20.WAV'),
    not full paths.
    """
    with open(pgm_path, "rb") as f:
        data = f.read()

    if b"MPC1000 PGM" not in data[4:20]:
        raise ValueError(f"Not a valid MPC1000 PGM file: {pgm_path}")

    wavs = []
    for i in range(PGM_PAD_COUNT):
        offset = PGM_PAD_OFFSET + i * PGM_PAD_SIZE
        block = data[offset : offset + PGM_PAD_SIZE]
        sample_name = block[0:16].rstrip(b"\x00").decode("ascii", errors="replace")
        if sample_name:
            wav = sample_name + ".WAV"
            if wav not in wavs:
                wavs.append(wav)

    return wavs


def seq_to_wavs(seq_path: str) -> dict:
    """
    Given a SEQ file path, find all WAV files it depends on.

    Looks for PGM and WAV files in the same directory as the SEQ file.

    Returns a dict with:
      'pgms'    - list of PGM filenames referenced by the sequence
      'wavs'    - deduplicated list of WAV filenames referenced by those PGMs
      'missing' - PGM or WAV filenames that could not be found on disk
    """
    seq_dir = os.path.dirname(os.path.abspath(seq_path))

    # Build a case-insensitive filename map for the directory
    dir_files = {name.upper(): name for name in os.listdir(seq_dir)}

    pgm_names = parse_seq(seq_path)

    all_wavs = []
    missing = []

    for pgm_name in pgm_names:
        actual = dir_files.get(pgm_name.upper())
        if actual is None:
            missing.append(pgm_name)
            continue

        wavs = parse_pgm(os.path.join(seq_dir, actual))
        for wav in wavs:
            if wav not in all_wavs:
                all_wavs.append(wav)
            if dir_files.get(wav.upper()) is None:
                if wav not in missing:
                    missing.append(wav)

    return {
        "pgms": pgm_names,
        "wavs": all_wavs,
        "missing": missing,
    }


def dir_to_wavs(dir_path: str) -> dict:
    """
    Scan a directory for all SEQ files and return a combined dependency report.

    Returns a dict keyed by SEQ filename, each value being the result of
    seq_to_wavs() for that file. Also includes a top-level 'all_wavs' key
    with the deduplicated union of every WAV referenced across all sequences.
    """
    seq_files = sorted(
        f for f in os.listdir(dir_path) if f.upper().endswith(".SEQ")
    )

    results = {}
    all_wavs = []

    for seq_file in seq_files:
        seq_path = os.path.join(dir_path, seq_file)
        result = seq_to_wavs(seq_path)
        results[seq_file] = result
        for wav in result["wavs"]:
            if wav not in all_wavs:
                all_wavs.append(wav)

    results["all_wavs"] = all_wavs
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.SEQ | directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isdir(target):
        results = dir_to_wavs(target)
        all_wavs = results.pop("all_wavs")
        for seq_file, result in results.items():
            print(f"{seq_file}:")
            print(f"  PGMs: {', '.join(result['pgms']) or '(none)'}")
            print(f"  WAVs: {', '.join(result['wavs']) or '(none)'}")
            if result["missing"]:
                print(f"  Missing: {', '.join(result['missing'])}")
        print(f"\nAll WAVs across all sequences ({len(all_wavs)}):")
        for w in all_wavs:
            print(f"  {w}")
    else:
        result = seq_to_wavs(target)

        print(f"PGMs ({len(result['pgms'])}):")
        for p in result["pgms"]:
            print(f"  {p}")

        print(f"\nWAVs ({len(result['wavs'])}):")
        for w in result["wavs"]:
            print(f"  {w}")

        if result["missing"]:
            print(f"\nMissing from disk ({len(result['missing'])}):")
            for m in result["missing"]:
                print(f"  {m}")
