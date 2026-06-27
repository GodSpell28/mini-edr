# mini-edr

Lightweight endpoint monitoring concept in Python.

Tracks process creation, file changes, and network connections using standard OS libraries.

## Features

- Process creation/deletion monitoring
- File system change tracking
- Network connection logging
- Rule-based alerting
- JSON/JSONL event export
- CLI with configurable watch paths and alerts

## Requirements

- Python 3.8+
- psutil
- watchdog

## Installation

```bash
pip install -e .
```

## Usage

```bash
mini-edr --watch /tmp --interval 1.0 --alert-process cmd.exe powershell.exe
```

## Configuration

Default settings:

```json
{
  "watch_paths": ["."],
  "poll_interval": 2.0,
  "alert_processes": [],
  "output": "edr-events.jsonl"
}
```

## Project Structure

```
mini-edr/
├── src/mini_edr/
│   ├── __init__.py
│   ├── cli.py           # argparse CLI
│   ├── config.py       # JSON config loader/saver
│   ├── events.py       # event dataclasses and serialization
│   ├── monitor.py      # process, filesystem, network sampling
│   └── rules.py        # rule engine
├── tests/
│   └── test_monitor.py
└── docs/
    └── usage.md
```

## Limitations

Educational implementation only. No kernel-mode components, no tamper resistance, and no real-time blocking.

## License

MIT — see LICENSE for details.
