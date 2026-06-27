import json
import unittest

from mini_edr.events import (
    BaseEvent,
    ProcessEvent,
    FileEvent,
    NetworkEvent,
    event_to_json,
)
from mini_edr.rules import RuleEngine


class TestEvents(unittest.TestCase):
    def test_process_event_json(self):
        event = ProcessEvent(pid=1, ppid=0, name="test", path="/bin/test")
        payload = json.loads(event_to_json(event))
        self.assertEqual(payload["event_type"], "process")
        self.assertEqual(payload["data"]["name"], "test")

    def test_file_event_json(self):
        event = FileEvent(path="/tmp/x", change_type="created")
        payload = json.loads(event_to_json(event))
        self.assertEqual(payload["event_type"], "file")

    def test_network_event_json(self):
        event = NetworkEvent("127.0.0.1", 1234, "10.0.0.1", 80, "tcp")
        payload = json.loads(event_to_json(event))
        self.assertEqual(payload["data"]["remote_port"], 80)


class TestRuleEngine(unittest.TestCase):
    def test_rule_fires(self):
        engine = RuleEngine()
        hits = []

        def predicate(event):
            return event["pid"] == 1

        def handler(event):
            hits.append(event)

        engine.add_rule("pid1", predicate, handler)
        engine.evaluate({"pid": 1, "name": "x"})
        self.assertEqual(len(hits), 1)

    def test_rule_ignores(self):
        engine = RuleEngine()
        hits = []

        def predicate(event):
            return False

        def handler(event):
            hits.append(event)

        engine.add_rule("never", predicate, handler)
        engine.evaluate({"pid": 2})
        self.assertEqual(len(hits), 0)


if __name__ == "__main__":
    unittest.main()
