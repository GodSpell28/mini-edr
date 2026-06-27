"""EDR monitor that watches processes, files, and network connections.""""

import time
from typing import Optional

from mini_edr.events import (
    BaseEvent,
    ProcessEvent,
    FileEvent,
    NetworkEvent,
    event_to_json,
)
from mini_edr.rules import RuleEngine


class EDRMonitor:
    def __init__(self, poll_interval: float = 2.0, watch_paths=None):
        self.poll_interval = poll_interval
        self.watch_paths = watch_paths or ["."]
        self.rules = RuleEngine()
        self._running = False

    def register_alert(self, name: str, predicate, handler):
        self.rules.add_rule(name, predicate, handler)

    def watch(self):
        self._running = True
        print("Starting EDR monitor...")
        try:
            while self._running:
                self._tick()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("Stopping EDR monitor")

    def stop(self):
        self._running = False

    def _tick(self):
        process_event = self._sample_processes()
        if process_event:
            self.rules.evaluate(process_event.data)

        file_event = self._sample_filesystem()
        if file_event:
            self.rules.evaluate(file_event.data)

        network_event = self._sample_network()
        if network_event:
            self.rules.evaluate(network_event.data)

    def _sample_processes(self) -> Optional[ProcessEvent]:
        try:
            import psutil
        except ImportError as exc:
            print(f"psutil required for process monitoring: {exc}")
            return None

        for proc in psutil.process_iter(["pid", "ppid", "name", "exe"]):
            try:
                info = proc.info
                return ProcessEvent(
                    pid=info["pid"],
                    ppid=info["ppid"],
                    name=info["name"],
                    path=info.get("exe") or "",
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def _sample_filesystem(self) -> Optional[FileEvent]:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError as exc:
            print(f"watchdog required for file monitoring: {exc}")
            return None

        handler = FileSystemEventHandler()

        for path in self.watch_paths:
            observer = Observer()
            observer.schedule(handler, path, recursive=False)
            observer.start()

        time.sleep(self.poll_interval)
        return FileEvent(path=self.watch_paths[0], change_type="polled")

    def _sample_network(self) -> Optional[NetworkEvent]:
        try:
            import psutil
        except ImportError as exc:
            print(f"psutil required for network monitoring: {exc}")
            return None

        for conn in psutil.net_connections(kind="tcp"):
            if conn.laddr and conn.raddr:
                return NetworkEvent(
                    local_addr=conn.laddr.ip,
                    local_port=conn.laddr.port,
                    remote_addr=conn.raddr.ip,
                    remote_port=conn.raddr.port,
                    proto="tcp",
                )
        return None
