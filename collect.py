"""
Collect all files needed by MPC 1000 SEQ sequences into an output directory.

Given a SEQ file (or a directory of SEQ files) and an output path, this script
resolves all referenced PGM and WAV files and copies everything needed to run
the sequence(s) on the MPC into a single flat folder.

Usage:
  python3 collect.py <file.SEQ> <output_dir>
  python3 collect.py <input_dir> <output_dir>
"""

import os
import shutil
import sys

from mpc1k import seq_to_wavs, dir_to_wavs


def collect_seq(seq_path: str, output_dir: str) -> dict:
    """
    Resolve all dependencies of a single SEQ file and copy them, plus the SEQ
    itself, into output_dir.

    Returns a dict with:
      'copied'  - list of filenames successfully copied
      'missing' - list of filenames that could not be found on disk
    """
    seq_dir = os.path.dirname(os.path.abspath(seq_path))
    dir_files = {name.upper(): name for name in os.listdir(seq_dir)}

    result = seq_to_wavs(seq_path)

    # Gather every file we need: the SEQ itself + all PGMs + all WAVs
    seq_filename = os.path.basename(seq_path)
    needed = [seq_filename] + result["pgms"] + result["wavs"]

    os.makedirs(output_dir, exist_ok=True)

    copied = []
    missing = list(result["missing"])  # already-known missing files

    for filename in needed:
        actual = dir_files.get(filename.upper())
        if actual is None:
            if filename not in missing:
                missing.append(filename)
            continue
        src = os.path.join(seq_dir, actual)
        dst = os.path.join(output_dir, actual)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        copied.append(actual)

    return {"copied": copied, "missing": missing}


def collect_dir(input_dir: str, output_dir: str) -> dict:
    """
    Resolve dependencies for every SEQ file in input_dir and copy all of them
    into output_dir.

    Returns a dict keyed by SEQ filename, each value being the result of
    collect_seq() for that file.
    """
    seq_files = sorted(
        f for f in os.listdir(input_dir) if f.upper().endswith(".SEQ")
    )

    results = {}
    for seq_file in seq_files:
        seq_path = os.path.join(input_dir, seq_file)
        results[seq_file] = collect_seq(seq_path, output_dir)

    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <file.SEQ | input_dir> <output_dir>")
        sys.exit(1)

    source, output_dir = sys.argv[1], sys.argv[2]

    if os.path.isdir(source):
        results = collect_dir(source, output_dir)
        total_copied = set()
        total_missing = set()
        for seq_file, result in results.items():
            total_copied.update(result["copied"])
            total_missing.update(result["missing"])
            status = f"{len(result['copied'])} files copied"
            if result["missing"]:
                status += f", {len(result['missing'])} missing"
            print(f"{seq_file}: {status}")
        print(f"\nTotal files in output: {len(total_copied)}")
        if total_missing:
            print(f"Could not find ({len(total_missing)}):")
            for m in sorted(total_missing):
                print(f"  {m}")
    else:
        result = collect_seq(source, output_dir)
        print(f"Copied ({len(result['copied'])}):")
        for f in result["copied"]:
            print(f"  {f}")
        if result["missing"]:
            print(f"\nCould not find ({len(result['missing'])}):")
            for m in result["missing"]:
                print(f"  {m}")
