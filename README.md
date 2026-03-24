# RAW CAN Log Converter

A desktop application for converting between common CAN bus log file formats. Built with Python and PyQt6, it provides a simple GUI for selecting input/output formats, browsing files, and converting with real-time progress feedback.

## Features

- Convert between **10 different CAN log formats**
- Batch convert multiple files at once (from a single folder)
- Real-time progress bar during conversion
- Automatic output file naming (`_out` suffix in the same directory)
- Overwrite confirmation for existing output files
- Supports standard CAN, extended (29-bit) IDs, and RTR frames

## Supported Formats

Any of the formats below can be used as either input or output:

| Format | Extension | Description |
|---|---|---|
| **PCAN .trc** | `.trc` | PEAK PCAN-View trace files (v2.1) |
| **CSS .csv** | `.csv` | CSS Electronics CSV log format |
| **CSS CLx000 .txt** | `.txt` | CSS Electronics CLx000 TXT log format |
| **MF4 Log .mf4** | `.mf4` | ASAM MDF4 measurement data format |
| **Busmaster .log** | `.log` | Busmaster CAN logger format |
| **Motec CAN Inspector .asc** | `.asc` | MoTeC CAN Inspector ASCII log |
| **Kvaser .asc** | `.asc` | Kvaser ASCII log format |
| **Racelogic .asc** | `.asc` | Racelogic VBOX ASCII log format |
| **RaceKeeper .csv** | `.csv` | RaceKeeper CSV log format |
| **SocketCAN .log** | `.log` | Linux SocketCAN candump log format |

## How It Works

All conversions go through **SocketCAN log format** as an intermediate representation. The input file is first parsed into SocketCAN format, then written out in the selected output format. This keeps the conversion logic modular and makes it straightforward to add new formats.

## Requirements

- Python 3
- [PyQt6](https://pypi.org/project/PyQt6/)
- [asammdf](https://pypi.org/project/asammdf/) (only required for MF4 format support)

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Select the **input format** that matches your log file
2. Click **Browse Input File** to select one or more files
3. Select the desired **output format**
4. Click **Convert**

Output files are saved in the same directory as the input files with `_out` appended to the filename.
