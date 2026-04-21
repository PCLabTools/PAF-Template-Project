---
name: paf-new-module
description: "Create a new PAF module from scratch. Use when: adding a module, creating a new module, new standard module, new factory module, new actor, scaffold module."
argument-hint: "<module-name> [standard|factory]"
---

# New PAF Module

Creates a fully wired PAF module — source files, `__init__.py` export, and `main.py` registration — from the project templates.

## When to Use
- "Create a new module called SensorReader"
- "Add a factory module named MotorController"
- "Scaffold a new standard PAF module"

## Inputs

Collect from the user before proceeding (ask if not provided in the invocation):

1. **Module name** — e.g. `SensorReader`. Used to derive:
   - `ClassName` = PascalCase of the name (e.g. `SensorReader`)
   - `module_name` = snake_case of the name (e.g. `sensor_reader`)
   - `module_address` = lowercase of the name (e.g. `sensor_reader`)
2. **Module type** — `standard` or `factory`
3. **Description** — one-line description for the module's docstring
4. **Author** — for the file header (default: `"Your Name (your.email@example.com)"`)

## Procedure

### Step 1 — Gather inputs

If the user has not provided the module name, ask now. Infer type from context if possible; otherwise ask. Default type is `standard`.

### Step 2 — Create the module folder

Create `src/paf/modules/<module_name>/` with these files:

#### For `standard` type:

**`module.py`** — copy from [./assets/standard_module.py](./assets/standard_module.py), replacing:
- `{{ClassName}}` → PascalCase class name
- `{{MODULE_DESCRIPTION}}` → user's description
- `{{AUTHOR}}` → author string

**`__init__.py`** — copy from [./assets/standard_init.py](./assets/standard_init.py), replacing:
- `{{ClassName}}` → PascalCase class name
- `{{module_name}}` → snake_case module name
- `{{AUTHOR}}` → author string

**`tests/__init__.py`** — create as an empty file.

**`tests/test_module.py`** — copy from [./assets/standard_test_module.py](./assets/standard_test_module.py), replacing:
- `{{ClassName}}` → PascalCase class name
- `{{module_name}}` → snake_case module name

**`scripts/run-tests.bat`** — copy from [./assets/run-tests.bat](./assets/run-tests.bat), replacing:
- `{{module_name}}` → snake_case module name

**`.gitignore`** — copy from [./assets/.gitignore](./assets/.gitignore) verbatim.

#### For `factory` type:

**`module.py`** — copy from [./assets/factory_module.py](./assets/factory_module.py), replacing all `{{ClassName}}` and `Base{{ClassName}}` placeholders.

**`simulated.py`** — copy from [./assets/factory_simulated.py](./assets/factory_simulated.py), replacing all `{{ClassName}}` and `Simulated{{ClassName}}` placeholders.

**`__init__.py`** — copy from [./assets/factory_init.py](./assets/factory_init.py), replacing all class name placeholders.

**`tests/__init__.py`** — create as an empty file.

**`tests/test_module.py`** — copy from [./assets/factory_test_module.py](./assets/factory_test_module.py), replacing:
- `{{ClassName}}` → PascalCase class name
- `Base{{ClassName}}` → `Base` + PascalCase class name
- `Simulated{{ClassName}}` → `Simulated` + PascalCase class name
- `Dummy{{ClassName}}` → `Dummy` + PascalCase class name
- `{{module_name}}` → snake_case module name

**`scripts/run-tests.bat`** — copy from [./assets/run-tests.bat](./assets/run-tests.bat), replacing:
- `{{module_name}}` → snake_case module name

**`.gitignore`** — copy from [./assets/.gitignore](./assets/.gitignore) verbatim.

### Step 3 — Register in `src/paf/modules/__init__.py`

Add the import and export. Example for standard:
```python
from .<module_name> import <ClassName>
```
Add `<ClassName>` to `__all__`.

For factory, also add `Base<ClassName>` and `Simulated<ClassName>`.

### Step 4 — Instantiate in `src/main.py`

Add the import at the top:
```python
from paf.modules import <ClassName>
```

Add instantiation in `Main.__init__()`:
```python
# Standard:
<ClassName>("<module_address>", self.protocol, debug=self.debug)

# Factory (assign to self if HTTP server needs reference, otherwise inline):
<ClassName>("<module_address>", self.protocol, debug=self.debug, implementation_type="simulated")
```

For factory type, also add a `send_action` call in `Main.run()` following the existing pattern.

### Step 5 — Factory-only: PyInstaller hidden import

For factory modules, remind the user to add to `scripts/build-exe.bat`:
```
--hidden-import paf.modules.<module_name>.simulated ^
```
(immediately after the existing `--hidden-import` lines)

### Step 6 — Confirm

List all files created/modified. Remind the user to:
- Fill in any `# TODO:` placeholders in the new module
- Run per-module tests: `src/paf/modules/<module_name>/scripts/run-tests.bat`
- Run all tests: `python -m unittest discover -s src -p "test_*.py"`

## Key Conventions (from codebase)

- `self.debug` **must** be set before `super().__init__()` — the base class accesses it during startup
- `handle_message` returns `True` to shutdown, `False` to keep running
- Unknown commands must call `super().handle_message(message)` (raises `NotImplementedError` for truly unknown commands)
- Module addresses are plain lowercase strings
- Factory implementations **must** call `<FactoryClass>.register("name", <ImplClass>)` at import time (bottom of `simulated.py`)
