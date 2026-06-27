# mini-edr — Interview Documentation

## 1. Project Overview

**mini-edr** is a lightweight, educational Endpoint Detection and Response (EDR) concept written in Python. It demonstrates the core architectural patterns of a real EDR system—process monitoring, filesystem watching, network connection tracking, and rule-based alerting—while remaining small enough to understand end-to-end.

**Why this project?**
- EDR platforms are complex and usually closed-source.
- Building a simplified version shows understanding of OS-level telemetry, event pipelines, modular design, and security trade-offs.
- It’s a concrete portfolio piece that translates abstract security concepts into runnable code.

---

## 2. High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Process   │     |  Filesystem   │     |   Network    │
│  Sampler    │     |   Watcher     │     |   Sampler    │
└──────┬──────┘     └──────┬───────┘     └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Rule Engine │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Monitor   │
                    │  (EDRMonitor)│
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Handlers   │
                    │  → JSON/JSONL│
                    └─────────────┘
```

**Data flow:**
1. `EDRMonitor` polls or watches three sources: processes, filesystem, network.
2. Each source produces a typed event (`ProcessEvent`, `FileEvent`, `NetworkEvent`).
3. Events are fed into `RuleEngine`.
4. Matching rules invoke handlers that log alerts or write JSONL output.

---

## 3. Core Components

### 3.1 Events (`src/mini_edr/events.py`)
- **BaseEvent**: common fields (`timestamp`, `event_type`, `source`, `data`).
- **ProcessEvent**: pid, ppid, name, path.
- **FileEvent**: path, change_type.
- **NetworkEvent**: local/remote address, ports, protocol.
- **Serialization**: `event_to_json()` converts events to JSON for export.

**Interview point:** I used `@dataclass` to enforce a schema. Every event has a stable shape, which makes downstream rules and log parsing predictable.

### 3.2 Rule Engine (`src/mini_edr/rules.py`)
- Maintains a list of `{name, predicate, handler}` rules.
- `evaluate(event)` runs all predicates; matching rules call their handler.
- Fail-safe: exceptions in one rule don’t crash the monitor.

**Interview point:** This is a minimal production-style pattern. Real EDRs use YARA, Sigma, or custom logic; my engine is the pedagogical equivalent—predicate/handler pairs that are composable and testable.

### 3.3 Monitor (`src/mini_edr/monitor.py`)
- `EDRMonitor` owns the sampling loop.
- `_sample_processes()`: uses `psutil.process_iter` to snapshot a single process.
- `_sample_filesystem()`: uses `watchdog.Observer` to watch paths.
- `_sample_network()`: uses `psutil.net_connections` for TCP snapshots.
- `watch()`: main loop; `_tick()` collects one sample of each source per interval.

**Interview point:** Polling vs. event-driven is a key EDR design choice. I mixed both: `psutil` for processes/network (snapshot-based), `watchdog` for filesystem (event-driven). I can discuss why—`psutil` is the simplest cross-platform way to enumerate PIDs/connections without root, while `watchdog` gives real-time FS events.

### 3.4 Configuration (`src/mini_edr/config.py`)
- `load_config(path)` reads JSON, merges with `DEFAULT_CONFIG`.
- `save_config(path, config)` persists settings.

**Interview point:** JSON is used for human-editable config. Merging with defaults means users only need to override what they care about.

### 3.5 CLI (`src/mini_edr/cli.py`)
- `argparse` with `--watch`, `--interval`, `--alert-process`, `--output`, `--version`.
- Wires monitor alerts to file handlers.
- Entry point: `mini-edr = "mini_edr.cli:main"` in `pyproject.toml`.

**Interview point:** A real EDR needs CLI and service modes. My CLI is the service-mode stub, built with stdlib `argparse` to avoid extra dependencies.

---

## 4. Design Decisions & Trade-offs

| Decision | Rationale | Trade-off |
|-----------|-----------|-----------|
| Python | Rapid prototyping, rich libraries (`psutil`, `watchdog`) | Slower than C for kernel-mode drivers |
| Polling + watchdog | Simple, cross-platform, no admin needed | Higher CPU/latency vs. kernel callbacks |
| JSONL output | Easy to tail, parse, ship to SIEM | Larger files than binary formats |
| Rule engine as predicates | Easy to unit-test, extend | Less powerful than compiled YARA/Sigma |
| Editable install (`pip install -e .`) | Fast iteration during development | Not suitable for distribution without wheel build |

---

## 5. Security & Limitations

**Known limitations (important to say in an interview):**
- **User-mode only**: real EDRs need kernel drivers for tamper resistance.
- **No blocking**: this logs; it doesn’t terminate processes or isolate endpoints.
- **Runs as standard user**: `psutil` may miss some processes on Windows without admin.
- **Sample-based**: `_sample_processes()` returns **one** random process per tick. A real monitor would diff against the previous snapshot to detect create/exit.
- **No authentication/encryption**: event export is plaintext.
- **Educational scope**: not production-hardened against log tampering or DoS.

**How I’d harden it:**
- Diff process lists between ticks to detect create/exit.
- Add digital signatures to event logs.
- Add a configurable output backend: JSONL, syslog, or HTTP.
- Support Windows ETW or eBPF on Linux for lower-overhead telemetry.

---

## 6. Testing

- `tests/test_monitor.py`: unit tests for event serialization and rule engine.
- `test_smoke.py`: integration-style smoke test verifying install + import path.
- Run with:
  ```bash
  pip install -e .
  python test_smoke.py
  ```

---

## 7. Packaging

- `pyproject.toml` with `setuptools` backend.
- `src` layout for clean imports.
- Declared dependencies: `psutil`, `watchdog`.
- Entry point exposes `mini-edr` CLI.
- License: MIT.

---

## 8. How to Demo in 2 Minutes

1. **Install:**
   ```bash
   pip install -e .
   ```
2. **Run CLI:**
   ```bash
   mini-edr --watch . --interval 2.0 --output demo.jsonl
   ```
3. **Trigger a file change** in the watched folder.
4. **Tail output:**
   ```bash
   Get-Content demo.jsonl -Wait
   ```
5. **Show code:** open `src/mini_edr/monitor.py` and point out:
   - `_sample_processes()` → `ProcessEvent`
   - `_sample_filesystem()` → `FileEvent`
   - `_sample_network()` → `NetworkEvent`
   - `RuleEngine.evaluate()`

---

## 9. What I Learned

- Cross-platform OS telemetry in Python is straightforward with `psutil` but has permission edge cases.
- Separation of **events** from **rules** from **output** makes the pipeline testable and extensible.
- Packaging a `src`-layout Python project with an entry point is trivial, but getting the import path right in tests on Windows requires care.
- Real EDR difficulty isn’t the logging—it’s the tamper resistance, performance, and noise reduction.

---

## 10. Roadmap (if this were a real project)

1. **Process diffing**: maintain a running process map; detect create/exit/network-open.
2. **Sigma rules support**: translate Sigma conditions into `RuleEngine` predicates.
3. **eBPF/ETW backend**: optional high-performance telemetry source.
4. **REST/HTTPS egress**: ship events to a central collector.
5. **Plugin loader**: dynamic rule loading from a `plugins/` folder.
6. **Service install**: Windows service / Linux systemd unit for the CLI.
