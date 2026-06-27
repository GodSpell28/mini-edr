# Usage

## CLI

Run the monitor from the command line:

```bash
mini-edr --watch . --interval 2.0 --alert-process cmd.exe powershell.exe
```

Output is written to `edr-events.jsonl` by default.

## Python API

```python
from mini_edr.monitor import EDRMonitor

def alert_handler(event):
    print("Alert:", event)

monitor = EDRMonitor(poll_interval=2.0, watch_paths=["."])

monitor.register_alert(
    name="suspicious_process",
    predicate=lambda event: event.get("name") in ["cmd.exe", "powershell.exe"],
    handler=alert_handler,
)

monitor.watch()
```

## Configuration

Save settings to `mini-edr.json`:

```json
{
  "watch_paths": ["."],
  "poll_interval": 2.0,
  "alert_processes": ["cmd.exe"],
  "output": "edr-events.jsonl"
}
```
