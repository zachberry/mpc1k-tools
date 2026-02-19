# MPC 1000 Tools

These were created with the assistance of Claude to help me with a few common tasks I do with my MPC 1000 (using JJOS OS3). Note that these may not work with the stock OS - I'm unsure if there's a difference in the SEQ and PGM files created with JJOS and with the stock OS.

## Documentation

The SEQ and PGM files are documented in Sequence.MD and Program.MD. These were generated with Claude Code - I can't verify that they are 100% accurate, so use at your own risk.

## Commands

### Removing unnecessary samples

A common thing that I'll do is create a bunch of sequences while I'm working on a set. Some of these evolve to full-featured tracks, but others don't go anywhere. Eventually as these collection of tracks evolve I end up wanting a streamlined setup where any unfinished or incomplete sequences are removed. However it can be difficult to determine which programs and sample files are referenced in the sequence files you want to keep.

This command will duplicate a folder but will only copy over referenced program (PGM) and sample (wav) files. The idea is that you'll delete any SEQ files that you don't want, then run this command to produce a new folder with unused files removed.

The content is duplicated to avoid any accidental deletions.

#### To run this on a directory:

```sh
python3 collect.py <input_dir> <output_dir>
```

#### To run it on an individual SEQ file:

```sh
python3 collect.py <file.SEQ> <output_dir>
```

### Reporting

To get a list of programs and samples that a sequence file uses you can use the `mpc1k.py` script.

#### To get a report on a directory:

```sh
python3 mpc1k.py <dir>
```

#### To get a report on an individual SEQ file:

```sh
python3 mpc1k.py <file.SEQ>
```

## Contributing and Use

I quickly generated this code to serve the functions I needed that are described above. Feel free to submit PRs to improve upon what's here!

This code is released under MIT License - Please feel free to do as you wish with this code!
