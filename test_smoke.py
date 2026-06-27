import sys, json
sys.path.insert(0, 'src')

from mini_edr.events import ProcessEvent, FileEvent, NetworkEvent, event_to_json
from mini_edr.rules import RuleEngine

pe = ProcessEvent(pid=1, ppid=0, name='x', path='/bin/x')
fe = FileEvent(path='/tmp/x', change_type='created')
ne = NetworkEvent('127.0.0.1', 5000, '10.0.0.5', 443, 'tcp')
assert json.loads(event_to_json(pe))['event_type'] == 'process'
assert json.loads(event_to_json(fe))['data']['change_type'] == 'created'
assert json.loads(event_to_json(ne))['data']['remote_port'] == 443

re = RuleEngine()
hits = []
re.add_rule('ok', lambda e: True, lambda e: hits.append(e))
re.evaluate({'x': 1})
assert len(hits) == 1

print('smoke ok')
