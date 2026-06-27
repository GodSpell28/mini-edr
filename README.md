# mini-edr

Lightweight endpoint monitoring concept in Python.

Tracks process creation, file changes, and network connections using standard OS libraries.

## Features

- Process creation/deletion monitoring
- File system change tracking
- Network connection logging
- Simple rule-based alerting
- JSON-formatted event export

## Requirements

- Python 3.8+

## Installation

```bash
git clone https://github.com/GodSpell28/mini-edr.git
cd mini-edr
pip install -e .
```

## Quick Start

```python
from mini_edr.monitor import EDRMonitor

monitor = EDRMonitor()
monitor.watch()
```

## Limitations

This is an educational implementation. It does not provide the tamper resistance, kernel-mode components, or real-time blocking of a production EDR.

## License

MIT — see LICENSE for details.
