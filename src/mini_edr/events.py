import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class BaseEvent:
    timestamp: str
    event_type: str
    source: str
    data: dict

    @classmethod
    def now(cls, event_type: str, source: str, data: dict):
        return cls(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            source=source,
            data=data,
        )


@dataclass
class ProcessEvent(BaseEvent):
    def __init__(self, pid: int, ppid: int, name: str, path: str):
        super().__init__(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type="process",
            source="os_monitor",
            data={
                "pid": pid,
                "ppid": ppid,
                "name": name,
                "path": path,
            },
        )


@dataclass
class FileEvent(BaseEvent):
    def __init__(self, path: str, change_type: str):
        super().__init__(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type="file",
            source="filesystem_watchdog",
            data={
                "path": path,
                "change_type": change_type,
            },
        )


@dataclass
class NetworkEvent(BaseEvent):
    def __init__(self, local_addr: str, local_port: int, remote_addr: str, remote_port: int, proto: str):
        super().__init__(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type="network",
            source="netstat_snapshot",
            data={
                "local_addr": local_addr,
                "local_port": local_port,
                "remote_addr": remote_addr,
                "remote_port": remote_port,
                "proto": proto,
            },
        )


def event_to_json(event: BaseEvent) -> str:
    return json.dumps(asdict(event))
