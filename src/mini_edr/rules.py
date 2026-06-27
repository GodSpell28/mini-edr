"""Simple rule-based alerting for EDR events."""

from typing import Callable, Dict, Any


AlertHandler = Callable[[Dict[str, Any]], None]


class RuleEngine:
    def __init__(self):
        self._rules = []

    def add_rule(self, name: str, predicate, handler: AlertHandler):
        self._rules.append({"name": name, "predicate": predicate, "handler": handler})

    def evaluate(self, event: Dict[str, Any]) -> None:
        for rule in self._rules:
            try:
                if rule["predicate"](event):
                    rule["handler"](event)
            except Exception as exc:
                print(f"Rule '{rule['name']}' failed: {exc}")
