# Usage

## Running the monitor

```python
from mini_edr.monitor import EDRMonitor

def alert_handler(event):
    print("Alert:", event)

monitor = EDRMonitor(poll_interval=2.0)

monitor.register_alert(
    name="suspicious_process",
    predicate=lambda event: event.get("name") in ["cmd.exe", "powershell.exe"],
    handler=alert_handler,
)

monitor.watch()
```

## Extending rules

Rules are simple predicate/handler pairs. Build custom detection logic in `src/mini_edr/rules.py`.
