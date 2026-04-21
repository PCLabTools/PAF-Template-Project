# PAF Template Project

A starting point for building **multi-threaded Python applications** using the **Python Agent Framework (PAF)** — a lightweight, message-passing framework that lets independent modules communicate with each other through a unified protocol.

---

## Overview

Modern applications often need to run multiple tasks concurrently — reading sensors, processing data, serving a UI, logging — without these concerns tangling together. PAF solves this by giving each concern its own **module**: a self-contained unit running in its own thread, communicating only through messages.

This template project provides:

- A pre-wired application entry point (`src/main.py`)
- The PAF communication library (`src/paf/communication/`)
- A working example module (`HelloWorld`)
- A module scaffold system powered by GitHub Copilot skills

---

## How It Works

### Modules

Each module is a class that extends `Module` and runs in its own thread. Modules do not call each other directly — they send messages.

```
┌──────────┐        ┌──────────┐        ┌──────────┐
│  Main    │        │ Module A │        │ Module B │
│ (thread) │──────▶ │ (thread) │──────▶ │ (thread) │
└──────────┘  msg   └──────────┘  msg   └──────────┘
```

### Protocol

The `Protocol` is the message bus. Every module registers with it at startup and is assigned an address. Any part of the application can send a message to any module by address.

```python
protocol.send_action("sensor_reader", "read", {"channel": 1})
```

### Messages

A `Message` carries a destination address, a command string, and an optional data payload. Messages are delivered via a thread-safe priority queue — one per module address.

```python
Message(address="sensor_reader", command="read", data={"channel": 1})
```

### Module Types

| Type | Description |
|---|---|
| **Standard** | Extends `Module` directly. Simple, single-implementation modules. |
| **Factory** | Uses a factory pattern with a `Base<Name>` ABC and swappable implementations (e.g. `Simulated<Name>` for testing). |

---

## Project Structure

```
src/
├── main.py                        # Application entry point
└── paf/
    ├── communication/             # PAF framework (git submodule)
    │   ├── message.py             # Message class
    │   ├── protocol.py            # Protocol (message bus)
    │   └── module.py              # Module base class
    └── modules/
        ├── __init__.py            # Public module exports
        └── hello_world/           # Example standard module
            ├── module.py
            ├── __init__.py
            ├── tests/
            └── scripts/
scripts/
    └── build-exe.bat              # PyInstaller build script
```

---

## Getting Started

### 1. Clone with submodules

```bash
git clone --recurse-submodules <repo-url>
```

Or if already cloned:

```bash
git submodule update --init --recursive
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python src/main.py
```

### 5. Run the tests

```bash
python -m unittest discover -s src -p "test_*.py"
```

You can also run tests directly from Copilot Chat using the `/paf-test` prompt, which discovers all module tests, runs them, and returns a formatted report with a summary table, per-module details, and failure output. Type `/paf-test` in the chat panel, or target a specific module:

```
/paf-test hello_world
```

---

## Adding and Removing Modules

This project includes GitHub Copilot skills that automate module management. See the [Developer Guide](#developer-guide-using-paf-copilot-skills) below for full details.

**Quick reference:**

| Task | Skill |
|---|---|
| Create a new module | `paf-new-module` |
| Remove a module | `paf-remove-module` |
| Add a module from git | `paf-pull-module` |
| Run all tests | `test-runner` agent |
| Test report in chat | `/paf-test` prompt |

---

## Building an Executable

```bat
scripts\build-exe.bat
```

Produces a standalone `.exe` in `dist/` via PyInstaller.

> If your project includes factory modules, ensure each has a `--hidden-import paf.modules.<module_name>.simulated` line in the build script — PyInstaller cannot detect dynamic registrations automatically.

---

---

# Developer Guide: Using PAF Copilot Skills

This project includes a set of GitHub Copilot skills that automate common PAF module tasks directly from the chat panel. This guide explains what each skill does and how to invoke it.

---

## How to Invoke a Skill

Open the Copilot Chat panel in VS Code and attach the skill's prompt file using the `#` file reference, then describe your intent. The simplest form is:

```
Follow instructions in #prompt:SKILL.md with these arguments: <args>
```

Each skill also has a natural-language description that allows Copilot to invoke it automatically when you describe what you want — e.g. _"create a new module called SensorReader"_ will trigger `paf-new-module` without needing to attach the file manually.

---

## Available Skills

### 1. `paf-new-module` — Create a new module

**File:** `.github/skills/paf-new-module/SKILL.md`

Creates a fully wired PAF module from scratch: generates all source files, registers the export in `src/paf/modules/__init__.py`, and instantiates it in `src/main.py`.

**Arguments:**
- Module name (PascalCase)
- Module type: `standard` or `factory`
- Description _(optional — will ask if omitted)_
- Author _(optional — defaults to placeholder)_

**Examples:**

```
Follow instructions in #prompt:SKILL.md with these arguments: SensorReader standard
```

```
Follow instructions in #prompt:SKILL.md with these arguments: MotorController factory
```

**What gets created** (standard example for `SensorReader`):

| File | Description |
|---|---|
| `src/paf/modules/sensor_reader/module.py` | Module class with `handle_message` and `background_task` |
| `src/paf/modules/sensor_reader/__init__.py` | Public export |
| `src/paf/modules/sensor_reader/tests/test_module.py` | Unit tests |
| `src/paf/modules/sensor_reader/tests/__init__.py` | Test package marker |
| `src/paf/modules/sensor_reader/scripts/run-tests.bat` | Per-module test runner |
| `src/paf/modules/sensor_reader/.gitignore` | Ignores `__pycache__` |

**What gets modified:**

- `src/paf/modules/__init__.py` — adds `from .sensor_reader import SensorReader` and updates `__all__`
- `src/main.py` — adds import, instantiation in `__init__`, and `send_action` call in `run()`

> **Factory modules** additionally generate `simulated.py` and `Base`/`Simulated` class variants, and prompt you to add a `--hidden-import` line to `scripts/build-exe.bat`.

---

### 2. `paf-remove-module` — Remove a module

**File:** `.github/skills/paf-remove-module/SKILL.md`

Safely removes a PAF module — deletes its folder and strips all references from `__init__.py` and `main.py`. Handles both regular folders and git submodules correctly.

**Arguments:**
- Module name

> ⚠️ Built-in modules (`standard_template`, `factory_template`, `webserver`) trigger an explicit confirmation prompt before proceeding.

**Examples:**

```
Follow instructions in #prompt:SKILL.md with these arguments: SensorReader
```

```
Follow instructions in #prompt:SKILL.md with these arguments: webserver
```

**What happens:**

1. Confirms the module exists
2. Detects whether it is a git submodule (`git submodule status`)
   - **Submodule:** runs `git submodule deinit -f` + `git rm -f` (updates `.gitmodules` and `.git/config`)
   - **Regular folder:** runs `Remove-Item -Recurse -Force`
3. Removes the import from `src/paf/modules/__init__.py`
4. Removes the import, instantiation, and any `send_action` calls from `src/main.py`
5. For factory modules: reminds you to remove the `--hidden-import` line from `scripts/build-exe.bat`

---

### 3. `paf-pull-module` — Add a module from a git repository

**File:** `.github/skills/paf-pull-module/SKILL.md`

Pulls a remote PAF module as a git submodule, then registers and instantiates it — the reverse of `paf-remove-module`.

**Arguments:**
- Git repository URL
- Folder name _(optional — inferred from the repo name by default)_

**Examples:**

```
Follow instructions in #prompt:SKILL.md with these arguments: https://github.com/PCLabTools/PAF-Module-Simple-Web-Server.git
```

```
Follow instructions in #prompt:SKILL.md with these arguments: https://github.com/PCLabTools/PAF-Module-Standard-Template.git standard_template
```

**What happens:**

1. Runs `git submodule add <url> src/paf/modules/<module_name>`
2. Reads the module's `__init__.py` to discover exported class names
3. Registers in `src/paf/modules/__init__.py`
4. Adds import and instantiation to `src/main.py`
5. For factory modules: reminds you to add `--hidden-import` to `scripts/build-exe.bat`

---

## Naming Conventions

| Input | Convention | Example |
|---|---|---|
| Module name argument | PascalCase | `SensorReader` |
| Folder name | snake_case | `sensor_reader` |
| Module address (in `main.py`) | snake_case | `"sensor_reader"` |
| Class name (in Python files) | PascalCase | `SensorReader` |

---

## Key Rules (from the codebase)

- `self.debug` **must** be assigned before `super().__init__()` in any module — the base class accesses it during startup.
- `handle_message` returns `True` to shut down the module, `False` to keep running.
- Unknown commands must be forwarded: `return super().handle_message(message)` (raises `NotImplementedError` for truly unknown commands).
- Factory implementations must self-register at import time: `FactoryClass.register("simulated", SimulatedClass)` at the bottom of `simulated.py`.
- After adding a factory module, add `--hidden-import paf.modules.<module_name>.simulated ^` to `scripts/build-exe.bat` — PyInstaller cannot detect dynamic registrations automatically.
