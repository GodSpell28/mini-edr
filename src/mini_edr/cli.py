"""Command-line interface for mini-edr."""

import argparse
import json
import sys
import time
from typing import List, Optional

from mini_edr.monitor import EDRMonitor
from mini_edr.events import ProcessEvent, FileEvent, NetworkEvent, event_to_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mini-edr",
        description="Lightweight endpoint monitoring concept.",
    )
    parser.add_argument(
        "--watch",
        nargs="+",
        default=["."],
        help="Filesystem paths to monitor for changes.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds (default: 2.0).",
    )
    parser.add_argument(
        "--alert-process",
        nargs="+",
        default=[],
        help="Process names that should trigger alerts.",
    )
    parser.add_argument(
        "--output",
        default="edr-events.jsonl",
        help="JSONL file for logged events (default: edr-events.jsonl).",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit.",
    )
    return parser


def _process_alert_handler(output_path: str):
    def handler(event):
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"alert": True, "event": event}) + "\n")
        print("[ALERT] process:", event.get("name"))

    return handler


def _log_all_handler(output_path: str):
    def handler(event):
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(event_to_json(event) + "\n")

    return handler


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from mini_edr import __version__
        print(__version__)
        return 0

    monitor = EDRMonitor(poll_interval=args.interval, watch_paths=args.watch)

    for name in args.alert_process:
        monitor.register_alert(
            name=f"alert_{name}",
            predicate=lambda event, n=name: event.get("name") == n,
            handler=_process_alert_handler(args.output),
        )

    monitor.register_alert(
        name="log_all",
        predicate=lambda event: True,
        handler=_log_all_handler(args.output),
    )

    monitor.watch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
