# Write additional pytest tests for the module mac_address of the validators package (source: targets/validators/src/validators/mac_address.py). Put them in targets/validators/tests/b1/mac_address/test_mac_address_b1.py and make sure they pass with `python -B -m pytest -q tests/b1/mac_address/`, run inside targets/validators with its .venv activated. Do not spawn subagents. Do not read anything under results/, dataset/, docs/ or targets/validators/tests/mh/.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Write additional pytest tests for the module mac_address of the validators package (source: targets/validators/src/validators/mac_address.py). Put them in targets/validators/tests/b1/mac_address/test_mac_address_b1.py and make sure they pass with `python -B -m pytest -q tests/b1/mac_address/`, run inside targets/validators with its .venv activated. Do not spawn subagents. Do not read anything under results/, dataset/, docs/ or targets/validators/tests/mh/.

---

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **list_files** — targets/validators/tests/b1/mac_address

> 🔧 **read_file** — targets/validators/src/validators/mac_address.py

### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — targets/validators/tests/b1

### 🤖 Assistant

> 🔧 called: write_file

Now I have a clear picture. Let me write the test file:

> 🔧 **write_file** — targets/validators/tests/b1/mac_address/test_mac_address_b1.py

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .venv\Scripts\python.exe -B -m pytest -q tests/b1/mac_address/

### 🤖 Assistant

All 27 tests pass. Here's a summary of what was written in [`test_mac_address_b1.py`](targets/validators/tests/b1/mac_address/test_mac_address_b1.py):

**Valid cases (13 tests)**
- Colon-separated addresses: lowercase, uppercase, and mixed-case (docstring example)
- Hyphen-separated addresses: lowercase, uppercase
- Edge values: all-zeros (`00:00:…`) and all-`FF` broadcast addresses, with both separators
- Typical hex digit addresses with both separators

**Invalid cases (14 tests)**
- Too few groups (5 octets, both separators) — including the docstring example
- Too many groups (7 octets)
- Mixed separators (`:` and `-` in the same string)
- Empty string
- No separator (12 hex chars concatenated)
- Dot separator
- Short/long octet (1 or 3 hex digits in a group)
- Non-hex character (`G`)
- Space separator
- Trailing/leading separator
- Plain text
- Leading whitespace