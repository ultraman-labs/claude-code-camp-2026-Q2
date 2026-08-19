# Python Step 9 — Global Executable

## 1. Objective

Port the Ruby `09_global_executable` milestone to Python. The completed step must
turn the Step 8 REPL into an installable package that exposes a `boukensha`
command independently of the current working directory. It must retain the
existing interactive behavior while adding package metadata, an executable
entry point, and a small bootstrap/composition boundary.

The command should use the packaged Step 9 implementation by default and provide
an explicitly documented way to select a source-tree step, if that capability is
retained in the Python port. This is a packaging and startup milestone, not a new
agent, tool, prompt, or conversation feature.

## 2. Known-Good Baseline

The baseline is `week1_baseline/python/08_the_repl_loop`. Preserve its public
`boukensha.run(...)` and `boukensha.repl(...)` APIs, shared REPL context/registry/
client/logger behavior, tool registration, conversation persistence, and commands
`/quiet`, `/loud`, `/clear`, `/help`, `/exit`, `/quit`, EOF, and Ctrl-C.

Copy the Step 8 tree as the starting point for Step 9. Existing implementation
files should not be refactored merely to make packaging look different. Changes
listed below are limited to behavior evidenced by the Ruby delta.

## 3. Ruby Step 8 → Step 9 Semantic Delta

The directory names in the Ruby README are off by one (`09_global_executable`
contains a README headed “Step 8” and describes the latest bundled release as
step 8). The authoritative behavior is the directory contents, version `0.9.0`,
and the Step 8 → Step 9 diff.

### Package and executable surface

**Ruby change**

`boukensha.gemspec` is added; `Gemfile` adds `gemspec`; the gem declares its
files, version, `bin` directory, and `boukensha` executable. `bin/boukensha`
adds a Ruby shebang, puts the gem `lib` directory on the load path, and invokes
`BoukenshaLoader.load_and_start_repl`.

→ **Architectural/behavioral purpose:** install the project as a gem and make a
stable command available on `$PATH`, rather than requiring a repository-local
runner.

→ **Python implication:** add native package metadata with a console-script
entry point named `boukensha`; the entry point must call a Python function and
return a useful process status. Do not translate the gemspec or introduce a
Ruby-style shim.

### Loader and step selection

**Ruby change**

`lib/boukensha_loader.rb` resolves `BOUKENSHA_PATH`, then `~/.boukensharc`, then
the gem's bundled `lib/boukensha.rb`. It validates that the selected folder has
`lib/boukensha.rb`, prints an optional debug line for `BOUKENSHA_DEBUG`, loads the
selected implementation, and aborts clearly when it lacks `repl`.

→ **Architectural/behavioral purpose:** separate executable startup from the
selected lesson implementation and preserve the teaching repository's ability
to run an earlier REPL-capable step.

→ **Python implication:** provide a small `loader`/bootstrap module only if the
same source-tree step selection is intentionally supported. It must validate
paths, avoid contaminating the installed import namespace, and call `repl()`
after loading. A Python package cannot directly import arbitrary sibling folders
that all contain the same `boukensha` package without an explicit isolated-load
strategy; this must not be approximated with a fragile `sys.path` mutation.
The simplest faithful default is packaged Step 9 plus a documented, tested
source-step loader, or packaged Step 9 only if compatibility is judged out of
scope.

### Configuration directory resolution

**Ruby change**

`Config#resolve_dir` removes the Step 8 fallback to `./.boukensha`. Step 9 now
uses `BOUKENSHA_DIR` when set, otherwise `~/.boukensha`. The loader's selected
code path (`BOUKENSHA_PATH`/`.boukensharc`) is deliberately separate from the
runtime configuration directory (`BOUKENSHA_DIR`).

→ **Architectural/behavioral purpose:** a globally launched command must not
silently change configuration because it was launched from a directory that
happens to contain `.boukensha`.

→ **Python implication:** modify `Config._resolve_dir` to remove the current
working-directory fallback, while retaining `BOUKENSHA_DIR` and the home default.
Keep code/step selection and runtime configuration as separate concerns.

### REPL presentation/config status

**Ruby change**

The banner stops reporting API-key presence and whether the config directory
exists. It reports separate `config`, `provider`, and `model` lines instead.

→ **Architectural/behavioral purpose:** avoid exposing key-status information in
the global command banner and make effective configuration clearer.

→ **Python implication:** update the Step 8 banner to the equivalent three-line
display, without changing command handling, context lifetime, or agent behavior.

### HTTP error wording

**Ruby change**

The special Ruby 401 “authentication failed” branch is removed; all unsuccessful
responses use the common retry/failure error path.

→ **Architectural/behavioral purpose:** normalize client errors in this snapshot;
this is not packaging behavior.

→ **Python implication:** inspect the Python client for an equivalent special 401
branch. If present, remove it to match the reference; if absent, make no change.

### Version and lock metadata

**Ruby change**

Version changes from `0.8.0` to `0.9.0`; the lockfile records the local gem and
updated platform/bundler metadata.

→ **Architectural/behavioral purpose:** identify the new release and resolve the
package as a local dependency.

→ **Python implication:** update `boukensha/version.py` to the Step 9 version and
put runtime dependencies/package data in the chosen Python metadata file. Do not
copy Ruby lockfile mechanics; generated Python lock/build files are classified
separately.

### Non-changes

The Ruby diff does not add tools, change agent construction, change prompts,
change persistence semantics, or alter the REPL command set. The Step 8 example
runner is absent from the packaged release because the command is now the
composition root. These are semantic boundaries, not invitations to redesign
the framework.

## 4. Step 9 Architecture

The proposed path is:

```text
installed `boukensha` console script
        ↓
Python cli.main()
        ↓
loader/bootstrap (resolve packaged default; optionally resolve a source step)
        ↓
boukensha.repl() composition root
        ↓
shared Config / Context / Registry / backend / PromptBuilder / Client / Logger
        ↓
REPL turns → Agent → tools/provider → persistent context
```

The user's model is accurate at a high level, but incomplete in two respects:
the command first enters a packaging-provided console-script wrapper, and the
loader is responsible for selecting/loading code before the REPL composition
root runs. Configuration loading is parallel to code selection, not a child step
folder: `BOUKENSHA_DIR` controls runtime state while `BOUKENSHA_PATH` (or the
optional rc file) controls implementation selection.

## 5. Proposed Python File Changes

| Python path | Action | Purpose | Ruby reference |
|---|---|---|---|
| `week1_baseline/python/09_global_executable/pyproject.toml` | CREATE | Package metadata, version, dependencies, package data, console script `boukensha` | `boukensha.gemspec`, `Gemfile` |
| `week1_baseline/python/09_global_executable/boukensha/cli.py` | CREATE | Console-script function and process-level startup | `bin/boukensha` |
| `week1_baseline/python/09_global_executable/boukensha/loader.py` | CREATE or explicitly omit after design decision | Validate/select implementation and bootstrap REPL | `lib/boukensha_loader.rb` |
| `.../boukensha/__init__.py` | MODIFY | Expose the selected public entry point/version only if needed | `lib/boukensha.rb` startup boundary |
| `.../boukensha/config.py` | MODIFY | Remove cwd `.boukensha` fallback | `config.rb` |
| `.../boukensha/repl.py` | MODIFY | Match Step 9 banner fields | `repl.rb` |
| `.../boukensha/client.py` | MODIFY only if a Python 401 special case exists | Match common HTTP error behavior | `client.rb` |
| `.../boukensha/version.py` | MODIFY | Set Step 9 version | `version.rb` |
| `.../README.md` | CREATE/MODIFY | Install, command, config/code-selection workflow | Ruby Step 9 README |
| `.../requirements.txt` | PRESERVE or MODIFY only to avoid dependency drift | Existing runtime dependency declaration; metadata must agree | Ruby Gemfile dependency intent |
| `.../prompts/system.md`, package modules, tasks, backends | PRESERVE | Step 8 runtime baseline | unchanged Ruby files |

The final create/modify decision for `loader.py` is an open design point,
recorded below; it must not be silently implemented as unsafe dynamic imports.

## 6. Packaging and Executable Strategy

Use a minimal `pyproject.toml` with a standard PEP 621 console-script entry:
`boukensha = "boukensha.cli:main"`. The entry function should initialize the
loader/default package and invoke the existing `boukensha.repl()`; it should not
duplicate composition-root logic.

The package must include Python modules and `prompts/system.md`. Dependencies
currently listed in Step 8 (`PyYAML`, `python-dotenv`) belong in package runtime
metadata as well as any transitional requirements file, with one authoritative
version policy.

Repository-local development remains possible with `python -m boukensha.cli`
or an editable install. The installed/global workflow is `pip install .` (or an
editable install during development), then `boukensha` from another directory.
The plan should not require a system-wide install or modify the user's shell.

If source-step switching is retained, the loader must use an isolated import
mechanism and require the target's package data, then verify a callable `repl`.
If that complexity is not supported by the curriculum's Python packaging model,
document the deliberate scope difference: the installed command loads its own
bundled Step 9 package, while older steps remain runnable from their own source
directories.

## 7. Configuration and Runtime Behavior

* **Configuration loading — CHANGE REQUIRED:** remove the cwd fallback in
  `Config._resolve_dir`, evidenced by Ruby `config.rb`. `BOUKENSHA_DIR` and
  `~/.boukensha` remain the sources of runtime settings and `.env`.
* **Environment variables — CHANGE REQUIRED:** preserve `BOUKENSHA_DIR`; add
  executable/loader handling for `BOUKENSHA_DEBUG` and, only if implemented,
  `BOUKENSHA_PATH`/the rc-file equivalent. These are startup controls, not
  provider settings.
* **Model/provider setup — NO STEP 9 CHANGE:** continue using Step 8 settings,
  environment API keys, and backend construction.
* **Logger state — NO STEP 9 CHANGE:** retain shared logger and `/quiet`/`/loud`.
* **`.boukensha` runtime/session state — CHANGE REQUIRED:** its location no
  longer falls back to the current directory; session semantics remain intact.
* **REPL behavior — CHANGE REQUIRED only for presentation:** update banner
  fields; preserve commands and turn loop.
* **Agent construction — NO STEP 9 CHANGE.**
* **Tool registration — NO STEP 9 CHANGE.**
* **Prompts — NO STEP 9 CHANGE.**
* **Session persistence — NO STEP 9 CHANGE:** preserve multi-turn context and
  `/clear` behavior.

## 8. Implementation Sequence

1. Create the Step 9 Python tree from the known-good Step 8 tree.
2. Confirm the intended Python packaging backend and package-data policy.
3. Add `pyproject.toml`, version `0.9.0`, and the console-script declaration.
4. Add `cli.py`; add and test `loader.py` only after resolving isolated loading.
5. Apply the evidenced config, banner, and (if applicable) 401-client deltas.
6. Update README installation and repository-local workflows.
7. Run static syntax/import checks without installing into the repository.
8. Build/install into a temporary virtual environment and verify the command
   from outside the source directory.
9. Run a controlled REPL session and regression checks for Step 8 behavior.
10. Classify build wheels, metadata, caches, logs, and `.boukensha` state before
    any future staging; inspect the milestone diff explicitly.

## 9. Verification Plan

Use a temporary virtual environment and temporary config directory for tests.
Proposed commands (to be executed during implementation, not now) are:

```bash
python -m compileall week1_baseline/python/09_global_executable/boukensha
PYTHONPATH=week1_baseline/python/09_global_executable python -c "import boukensha; print(boukensha.VERSION)"
python -m venv /tmp/boukensha-step9-venv
/tmp/boukensha-step9-venv/bin/pip install --no-cache-dir .
cd /tmp && /tmp/boukensha-step9-venv/bin/boukensha
```

For the interactive check, feed or type `/quiet`, `/loud`, `/clear`, a normal
task, `/exit`, and separately `/quit`; verify EOF and Ctrl-C exit cleanly. Verify
that a normal task reaches the configured Agent/provider and tool invocation,
that a second task sees prior context, and that `/clear` removes conversation
messages without removing registered tools.

Also verify `BOUKENSHA_DIR` from outside the source tree, debug output, malformed
or missing selected paths if a loader is implemented, and that a cwd `.boukensha`
is ignored. Run the Step 8 regression checks against the copied Step 9 tree and
compare public `run`/`repl` behavior.

## 10. Expected Runtime / Generated Artifacts

* **Source:** Python package modules, prompt files, README, and packaging metadata.
* **Packaging metadata:** `pyproject.toml`; optionally a committed lock file only
  if the repository's Python curriculum establishes that convention.
* **Build artifacts:** `dist/`, `build/`, `*.whl`, `*.tar.gz`, and `*.egg-info/`;
  normally temporary and excluded from the milestone commit.
* **Installed environment artifacts:** virtualenv directories, pip caches, and
  `__pycache__/`; never treat them as source.
* **Runtime/session state:** `~/.boukensha` or `BOUKENSHA_DIR` contents, logs,
  `.env`, settings, and any generated prompt/session files; keep out of the
  commit unless an explicit fixture is required.

## 11. Git Scope for the Future Milestone

The eventual commit will likely include the complete new
`week1_baseline/python/09_global_executable/` source snapshot, its
`pyproject.toml`, executable/bootstrap modules, README, prompts, and the small
runtime deltas documented above. It should exclude virtualenvs, caches, build
outputs, egg-info, logs, credentials, personal config, and runtime `.boukensha`
state. Do not stage or commit as part of this planning task.

## 12. Open Questions / Ambiguities

1. Should Python Step 9 faithfully support Ruby's arbitrary `BOUKENSHA_PATH`
   and `~/.boukensharc` source-step switching, or is the installed package's
   bundled default sufficient for the Python curriculum? The Ruby behavior is
   clear; the safe Python import mechanism is not established by existing files.
2. Which packaging backend and minimum Python version are curriculum policy? No
   Python Step 8 packaging metadata exists, so `pyproject.toml` details must be
   chosen consistently with repository conventions.
3. Should `requirements.txt` remain as a teaching artifact, be generated from
   metadata, or be removed? This plan preserves it pending repository policy.
4. Is version `0.9.0` required as an exact public compatibility value, or only a
   monotonic Step 9 marker? Ruby evidence strongly favors exact `0.9.0`.

## 13. Step 9 Acceptance Criteria

- [ ] **Implementation complete:** Step 9 tree contains the agreed metadata,
  console entry point, bootstrap decision, version, README, and evidenced runtime
  deltas; Step 8 APIs and behavior remain available.
- [ ] **Static verification complete:** compile/import checks pass and package
  data resolves without relying on the source cwd.
- [ ] **Installation/executable verification complete:** a temporary install
  exposes `boukensha`, and it launches from outside the source directory.
- [ ] **Runtime behavior complete:** REPL startup, configuration resolution,
  provider/Agent/tool invocation, multi-turn context, `/quiet`, `/loud`,
  `/clear`, `/exit`, `/quit`, EOF, and Ctrl-C work as specified.
- [ ] **Regression verification complete:** Step 8 commands, `run`, tool
  registration, persistence, and error handling have no unintended regressions.
- [ ] **Repository classification complete:** source, metadata, generated build
  outputs, installed artifacts, and runtime state are identified and separated.
- [ ] **Ready to stage:** only after explicit status/diff inspection confirms
  the intended Step 9 paths; staging and committing are separate authorized
  actions and are not part of this plan.
