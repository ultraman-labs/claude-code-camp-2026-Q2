# Python Step 10 — A Standard Tool Library

## 1. Scope and source authority

This is an implementation plan only. It contains no Step 10 implementation.

The Ruby Step 9 and Ruby Step 10 trees define the curriculum semantic delta:

- `week1_baseline/ruby/09_global_executable/`
- `week1_baseline/ruby/10_standard_tool_library/`

The Python implementation baseline is the completed Python Step 9 at commit
`7a328e6`, represented locally by:

- `week1_baseline/python/09_global_executable/`

Generated and packaging artifacts, including `boukensha-0.10.0.gem`, are not
semantic requirements. Instructor observations that are not encoded in Ruby
source are evidence notes or limitations, not automatic implementation
requirements.

The normal curriculum approach is to preserve Step 9 as a historical
iteration and construct a self-contained Step 10 directory by copying the
Step 9 tree, then applying only the documented delta.

## 2. Verified Ruby 09 -> 10 semantic delta

Ruby Step 10 supplies 34 standard tools:

- 6 filesystem tools: `pwd`, `list_directory`, `read_file`, `write_file`,
  `delete_file`, `search_files`.
- 1 shell tool: `run_command`.
- 27 MUD tools spanning connection, perception, movement, combat,
  communication, inventory/equipment, magic, and utility.

Filesystem and shell tools register automatically when `working_dir` is truthy.
`working_dir: false` disables them. Filesystem paths are normalized beneath a
single root; absolute paths and traversal outside that root return error
strings. `search_files` recursively applies a Ruby-regex-equivalent pattern
and returns `path:line_number:content` matches.

`run_command` executes in the working directory, defaults to a 30-second
timeout, combines stdout and stderr, reports empty output as `(no output)`,
adds `[exit N]` for nonzero status, and optionally checks the first command
token against `allowed_commands`.

MUD registration creates one shared session, auto-connects/logs in during
registration, exposes explicit `mud_connect`, `mud_disconnect`, and
`mud_status`, drains stale input before ordinary primitive calls, reads normal
responses through the prompt sentinel, and reserves quiet-read behavior for
`send_raw`. MUD registration is disabled by `mud: false`; omitted MUD options
are resolved from configuration when credentials/host are present.

The REPL banner adds configuration/API-key/provider and MUD status reporting.
The version progresses from `0.9.0` to `0.10.0`. Agent looping, Context
message history, Registry dispatch, providers/backends, and the DSL remain
semantically stable unless a concrete compatibility requirement forces an
adapter.

## 3. Python Step 9 architecture map

The following paths were inspected in the Python Step 9 baseline.

| Component | Step 9 evidence | Step 10 disposition |
|---|---|---|
| Public API and orchestration | `boukensha/__init__.py`, `run`, `repl` | MODIFY: add tool options and automatic registration while preserving provider/agent flow. |
| Context | `boukensha/context.py`, `Context` | MODIFY: add optional expanded `working_dir`; preserve messages/tools APIs. |
| Tool model | `boukensha/tool.py`, `Tool` | COPY UNCHANGED unless an exact schema serialization gap is found. |
| Registry | `boukensha/registry.py`, `Registry.tool`, `dispatch` | COPY UNCHANGED; standard modules call it directly. |
| Manual DSL | `boukensha/run_dsl.py`, `RunDSL` | COPY UNCHANGED; custom registration remains supported. |
| Agent | `boukensha/agent.py`, `Agent` | COPY UNCHANGED; retain generic exception-to-tool-result behavior. |
| REPL | `boukensha/repl.py`, `Repl` | MODIFY: accept tool/configuration state and show Step 10 status. |
| Configuration | `boukensha/config.py`, `Config` | MODIFY only for verified MUD/launcher precedence and typed options; preserve prompt loading. |
| Package API exports | `boukensha/__init__.py` | MODIFY to expose new registration modules/options as appropriate. |
| Filesystem tools | No standard module exists; Step 9 example has unsafe ad hoc tools | ADD NEW MODULE: standard filesystem registration. |
| Shell tools | No standard shell module exists | ADD NEW MODULE. |
| MUD compatibility | Ruby pre-week `week0_explore/mud_manager/` is the complete behavioral/protocol reference; `.agents/skills/mud-login/scripts/login.py` is a Python transport/login reference, not a package dependency | ADD NEW MODULES: package-local bounded Session/Primitives compatibility layer, then `tools/mud.py`. |
| CLI | `boukensha/cli.py` | MODIFY only for verified Step 10 launcher/MUD environment precedence. |
| Version | `boukensha/version.py` | MODIFY to `0.10.0`. |
| Packaging | `pyproject.toml`, `requirements.txt`, package data | MODIFY version/dependencies/package inclusion as required; preserve packaged `prompts/system.md`. |
| Example | `examples/example.py` | REPLACE with Step 10 demo semantics in the copied iteration. |
| README | `README.md` | REPLACE/update for the Step 10 tool library and limitations. |
| Backends | `boukensha/backends/` | COPY UNCHANGED; specifically retain OpenAI behavior. |
| Prompt resource | `boukensha/prompts/system.md` and `tasks/base.py` | COPY UNCHANGED; preserve Step 9 installed-package resource fix. |

The Step 9 example manually registers only `read_file` and
`list_directory`; those ad hoc registrations must not be mistaken for a
standard Step 10 implementation.

## 4. Proposed Python Step 10 file tree

The proposed iteration is:

```text
week1_baseline/python/10_standard_tool_library/
├── README.md                         # changed
├── examples/
│   └── example.py                    # changed/replaced demo
├── pyproject.toml                    # changed version/dependencies
├── requirements.txt                  # changed only if runtime dependency is confirmed
└── boukensha/
    ├── __init__.py                   # changed orchestration/public API
    ├── agent.py                      # copied unchanged
    ├── backends/                     # copied unchanged
    │   ├── __init__.py
    │   ├── anthropic.py
    │   ├── base.py
    │   ├── gemini.py
    │   ├── ollama.py
    │   ├── ollama_cloud.py
    │   └── openai.py
    ├── cli.py                         # changed only if launcher behavior requires it
    ├── client.py                     # copied unchanged
    ├── config.py                     # changed MUD/config resolution if needed
    ├── context.py                    # changed working_dir
    ├── errors.py                     # copied unless a minimal tool error is required
    ├── logger.py                     # copied unchanged
    ├── message.py                    # copied unchanged
    ├── prompt_builder.py             # copied unchanged
    ├── prompts/
    │   └── system.md                 # copied unchanged
    ├── registry.py                   # copied unchanged
    ├── repl.py                       # changed status/banner
    ├── run_dsl.py                   # copied unchanged
    ├── tasks/                        # copied unchanged
    │   ├── __init__.py
    │   ├── base.py
    │   └── player.py
    ├── tool.py                       # copied unchanged
    ├── mud/
    │   ├── __init__.py               # new compatibility boundary exports
    │   ├── session.py                # new Session/transport compatibility layer
    │   └── primitives.py              # new consumed stateless command builders
    ├── tools/
    │   ├── __init__.py               # new package export surface
    │   ├── file_system.py            # new standard module
    │   ├── shell.py                  # new standard module
    │   └── mud.py                    # new only after MUD boundary is resolved
    └── version.py                    # changed to 0.10.0
```

No Step 10 implementation directory may be created as part of this planning
phase. The tree above is the future target only.

## 5. Standard filesystem tool contract

The future `tools/file_system.py` should expose a registration function that
accepts a Python `Registry` and `working_dir`, then registers exactly these
six names.

| Name | Schema | Contract |
|---|---|---|
| `pwd` | `{}` | Return the expanded root path. |
| `list_directory` | `path: string = "."` | List sorted entries; directories end with `/`; empty directory returns `(empty)`. Non-directory and confinement failures return `error: ...`. |
| `read_file` | `path: string` | Return complete text. Non-file/read/confinement failures return `error: ...`. |
| `write_file` | `path: string, content: string` | Create missing parents, overwrite if present, return `ok: wrote N bytes to RELATIVE_PATH`. Failures return `error: ...`. |
| `delete_file` | `path: string` | Delete files only and return `ok: deleted PATH`; non-file/directory/confinement failures return `error: ...`. |
| `search_files` | `pattern: string, path: string = ".", glob: string = "*"` | Recursively search matching files and return newline-separated `path:line:content`; no match returns `no matches`; invalid pattern returns `error: invalid pattern: ...`. |

Use `pathlib` normalization and an explicit root-containment check. Preserve
the observable Ruby contract, including error strings and result formatting,
without reproducing Ruby APIs. Do not add a broader traversal abstraction or
additional filesystem operations.

## 6. Standard shell tool contract

The future `tools/shell.py` registers exactly `run_command`:

- Schema: `command: string`.
- Default timeout: 30 seconds.
- Execute with the configured working directory as `cwd`.
- `allowed_commands=None` permits all commands.
- Otherwise split the command as the Ruby implementation does and compare
  only its first whitespace-delimited token against the stringified allow-list.
- Capture combined stdout/stderr.
- Strip output before returning it.
- Empty output returns `(no output)`.
- Nonzero status appends `\n[exit N]`.
- Disallowed command returns the specified `error: ...` allow-list message
  without execution.
- Timeout returns `error: command timed out after Ns: COMMAND`.
- Missing executable and subprocess failures return `error: ...`.

Use an appropriate Python `subprocess` mechanism with a timeout; do not imitate
Ruby `Open3` literally. Do not add shell parsing or security redesign beyond
the Step 10 first-token behavior.

## 7. MUD integration plan

### Resolved source authority and compatibility decision

The instructor's pre-week MUD manager was found at
`week0_explore/mud_manager/`. Its `Session` and `Primitives` source is the
complete Ruby behavioral/protocol reference for the boundary consumed by Ruby
Step 10.

`.agents/skills/mud-login/scripts/login.py` is an existing Python TCP/Telnet
and login protocol reference. It is not a drop-in package dependency and must
not be imported from `.agents` as an accidental production dependency.
`.agents/skills/mud-explore/scripts/explore.py` is additional behavioral
evidence only.

No external Python `mud_manager` dependency has been identified or is required
at this point. The future implementation will use a small package-local
compatibility layer derived from the complete Ruby pre-week Session/Primitives
source, the Python `MudClient` transport/login lessons, and the exact
interface consumed by Ruby Step 10. This is a bounded compatibility port, not
a new MUD architecture.

The package-local boundary is:

- `boukensha/mud/session.py`: Session/transport state and reads;
- `boukensha/mud/primitives.py`: stateless command builders;
- `boukensha/tools/mud.py`: Boukensha Registry tool registration.

### Required registration surface

The package-local compatibility boundary must provide the following Session
behavior:

- construction with host and port;
- long-lived TCP connection, open/connect, open-state query, and close;
- host/port access;
- `send_command` with CRLF termination;
- login handling for name, password, Welcome, Reconnecting, Wrong password,
  and character-menu states;
- stale-buffer `drain`, prompt-oriented reads, and quiet-window reads;
- buffered-data preservation;
- Telnet IAC filtering;
- connection-close detection, timeout handling, and prompt-pattern matching.

It must preserve externally observable Ruby semantics without requiring Ruby's
literal Thread/Mutex/internal-buffer implementation.

The compatibility layer needs only these primitive methods, because these are
the methods consumed by the 27 Step 10 tools:

`look`, `examine`, `info_self`, `move`, `flee`, `set_position`, `track`,
`attack`, `skill_strike`, `consider`, `say_local`, `say_targeted`,
`say_channel`, `get`, `drop`, `put`, `equip`, `consume`, `cast`,
`use_magic_item`, `shop`, `practice`, and `save_char`.

The primitive layer must preserve exact command generation, argument ordering,
enum validation, required-string validation, optional-argument behavior, and
validation-error behavior. `send_raw` bypasses Primitives and uses Session
directly. Unused Ruby primitive methods must not be ported merely because they
exist.

Implementation may reuse or adapt compatible lessons from
`.agents/skills/mud-login/scripts/login.py`, especially socket lifecycle,
Telnet filtering, staged login, prompt matching, menu entry, and timeout/error
handling. Step 10 must own its runtime implementation inside its package; it
must not import `.agents` as a production dependency. It must add the shared
long-lived session semantics absent from the helper, including drain,
prompt-read, and quiet-read behavior.

Once this bounded Session/Primitives boundary exists, `tools/mud.py` must register
exactly these 27 names:

| Group | Tools and schema/defaults |
|---|---|
| Connection | `mud_connect {}`, `mud_disconnect {}`, `mud_status {}` |
| Perception | `look(target?: string, preposition?: string)`, `examine(target: string)`, `check(kind: string)` |
| Movement | `move(direction: string)`, `flee {}`, `set_position(position: string)`, `track(target: string)` |
| Combat | `attack(target: string, style: string = "kill")`, `skill_strike(skill: string, target: string)`, `consider(target: string)` |
| Communication | `say(text: string, mode: string = "say")`, `tell(target: string, text: string, mode: string = "tell")`, `channel_say(channel: string, text: string)` |
| Inventory/equipment | `get_item(item: string, container?: string, count?: integer)`, `drop_item(item: string, mode: string = "drop", count?: integer)`, `put_item(item: string, container: string, count?: integer)`, `equip_item(item: string, action: string, body_loc?: string)`, `consume_item(item: string, mode: string = "eat")` |
| Magic | `cast_spell(spell: string, target?: string)`, `use_magic_item(item: string, mode: string, target_args?: string)` |
| Utility | `shop(action: string, args?: string)`, `practice(skill?: string)`, `save_character {}`, `send_raw(command: string)` |

For every tool, preserve the Ruby primitive intent, exact name, schema, and
defaults. Ordinary gameplay calls must share one session, guard disconnected
state with `error: not connected — call mud_connect first`, drain stale input,
send the primitive command, and read through the MUD prompt sentinel. `send_raw`
must remain distinct: direct command send followed by quiet-read behavior.

Registration must auto-connect/login once. `mud_connect` must be safe when the
session is already open and report its current status rather than blindly
reconnecting. `mud_disconnect` and `mud_status` must retain their explicit
state behavior. Connection/primitive validation errors must become result
strings compatible with the Ruby behavior; unexpected exceptions must remain
compatible with the existing Agent's generic tool-error path.

Configuration precedence to plan:

1. Explicit `mud` options supplied to `run`/`repl`.
2. `mud=False` disables registration explicitly.
3. Otherwise use configured MUD host/port/username/password when the required
   host/username condition is present.
4. Preserve the Step 10 launcher behavior where legacy `MUD_NAME`,
   `MUD_HOST`, `MUD_PORT`, and `MUD_PASSWORD` override configuration, with a
   missing password producing the documented startup failure.

The absence of a third-party Python `mud_manager` is not itself a blocker.
The source-supported Welcome/Reconnecting/already-open behavior remains
distinct from the instructor-observed yes/no existing-session edge case, which
is not fully represented in source. No fix for that observation should be
invented unless required for the faithful Step 10 path.

## 8. Registration and startup flow

Future `run` and `repl` should follow this order:

1. Construct `Config` and resolve prompts/provider settings.
2. Construct `Context`, including `working_dir`.
3. Construct `Registry`.
4. If `working_dir` is enabled, automatically register FileSystem and Shell.
5. Resolve and, unless disabled, register MUD tools; auto-connect once.
6. Apply caller DSL customization.
7. Build the existing provider/client/Agent or REPL path.

The Python Step 9 global CLI is `boukensha/cli.py`, whose entry point calls
`boukensha.repl`. The bare command should continue to resolve through the
installed `project.scripts` entry point. Its semantic change is that the
default REPL now receives automatically registered tools and MUD environment
overrides; the package-resource behavior and installed global command must not
regress.

The future example should use the standard library rather than Step 9's
manual `configure_tools` callback. It should demonstrate the MUD task from the
Ruby example, while documenting the runtime configuration prerequisite. The
Ruby README says `demo.rb` while the supplied source is `example.rb`; retain
that evidence note and use the actual Python filename consistently unless the
curriculum explicitly resolves it.

## 9. Context / Config / REPL changes

### Context

Add an optional `working_dir` field, normalized to an absolute path when
provided. Preserve message/history, tool registration, `tool_count`, and
`turn_count` behavior.

### Configuration

Preserve `BOUKENSHA_DIR`, `.env`, YAML settings, user prompts, and packaged
`prompts/system.md` resolution. Add only the MUD and shell option plumbing
needed by Step 10. Do not regress the Step 9 package-resource fix that makes
the installed package load its bundled system prompt.

### Public run/repl options

Plan keyword options equivalent to:

- `working_dir`, defaulting to the current directory; `False` disables
  filesystem/shell registration.
- `allowed_commands`, default `None`.
- `shell_timeout`, default `30`.
- `mud`, default `None` for configuration resolution; `False` disables MUD.

### REPL

Extend the existing banner to show config path, provider/model, API-key set
status, and MUD configured/reachable status without performing a second MUD
login. Preserve `/clear`, `/quiet`, `/loud`, `/help`, `/exit`, `/quit`,
multi-turn history, and existing error display.

## 10. Components that must remain semantically stable

Unless direct Step 10 evidence requires an adapter, keep these compatible:

- `Agent` loop, iteration handling, tool-call processing, and generic
  error-to-tool-result behavior.
- `Context` messages/history and tool collection semantics.
- `Registry` names, schemas, dispatch, and unknown-tool behavior.
- Provider/backends, especially OpenAI request/response behavior.
- `RunDSL` custom tool registration.
- Packaged system-prompt loading and `pyproject.toml` package data.
- Global installation and `project.scripts` behavior.
- REPL command semantics and multi-turn context behavior.

## 11. Dependencies

Existing runtime dependencies are `PyYAML` and `python-dotenv`; reuse them.

No new third-party Python MUD dependency is currently planned. The bounded
compatibility layer should prefer Python standard-library facilities unless
implementation evidence proves another dependency necessary. Do not install
anything. The `.agents` helper is reference material, not a runtime package
dependency.

## 12. Documentation plan

The future Step 10 `README.md` should document:

- the curriculum purpose: a standard tool library;
- all three tool groups and the 34-tool count;
- filesystem confinement and result conventions;
- shell timeout and allow-list options;
- MUD configuration and shared-session assumptions;
- explicit MUD connection tools and auto-connect;
- `working_dir=False` and `mud=False` opt-outs;
- example usage and required runtime configuration;
- external MUD dependency assumptions;
- the `demo.rb` versus supplied `example.rb` filename discrepancy if it
  remains unresolved.

Do not silently fix or broaden instructor-documented limitations. Do not add
architectural improvements, stronger shell security, or traversal abstractions
not required by the Ruby source.

## 13. Implementation sequence

1. Copy Python Step 9 into the future Step 10 iteration, preserving Step 9.
2. Change version/package metadata and confirm package-resource inclusion.
3. Add `Context.working_dir` without changing history semantics.
4. Add and offline-test the six filesystem registrations and confinement.
5. Add and offline-test `run_command`, timeout, output, and allow-list rules.
6. Create the package-local Session compatibility layer.
7. Validate transport/login behavior offline where possible.
8. Create only the consumed Primitives surface.
9. Add shared-session MUD registration and the 27 tools.
10. Add automatic registration to `run` and `repl` with opt-outs.
11. Add REPL status/banner behavior without a duplicate login.
12. Update the example to exercise the intended Step 10 path.
13. Update README and package metadata documentation.
14. Run offline tests with fakes/mocks and regression tests.
15. Run live TBAMUD integration tests separately with an explicitly available
    MUD/runtime configuration.
16. Run provider/API tests only when credentials and network authorization are
    deliberately available.

## 14. Acceptance test matrix

### Offline tests

| ID | Future test |
|---|---|
| A | Build/install the package and verify the global `boukensha` entry point. |
| B | Verify automatic registration contains exactly 34 names: 6 filesystem, 1 shell, 27 MUD when MUD is configured. |
| C | Verify default/true `working_dir` registers the filesystem and shell groups with the expected root. |
| D | Verify `working_dir=False` registers neither filesystem nor shell tools. |
| E | Verify absolute paths and escaping `..` paths are rejected. |
| F | Verify all filesystem success, empty, non-file, non-directory, write, delete, and error contracts. |
| G | Verify `search_files` recursion, glob filtering, line numbering, regex failure, and `no matches`. |
| H | Verify shell success and combined stdout/stderr. |
| I | Verify shell nonzero exit annotation and empty-output behavior. |
| J | Verify shell timeout result. |
| K | Verify first-token `allowed_commands`, including rejection before execution. |
| L | Verify `mud=False` registers no MUD tools and does not connect. |
| U | Verify OpenAI backend regression without changing request/response semantics. |
| V | Verify multi-turn context/history behavior. |
| W | Verify `/clear`, `/quiet`, `/loud`, `/quit`, and `/exit`. |
| X | Verify installed-package loading of `prompts/system.md`. |
| T | Verify REPL banner/status formatting with mocked/no network status checks. |

### Offline MUD compatibility-boundary tests

Future deterministic tests should cover:

- Session open/close state;
- CRLF command sending;
- Telnet IAC filtering;
- login prompt progression;
- Welcome path;
- Reconnecting path;
- Wrong-password result;
- character-menu entry;
- buffered-read preservation;
- drain behavior;
- prompt-sentinel reads;
- quiet-window reads;
- timeout behavior;
- remote close behavior;
- primitive command generation;
- primitive validation failures;
- shared-session identity across all MUD tools.

### MUD-runtime tests

These require an available MUD server and the approved Python session/primitives
dependency:

| ID | Future test |
|---|---|
| M | Configured MUD options register the complete 27-tool group and auto-connect. |
| N | All tools use one shared session object/connection. |
| O | `mud_connect`, `mud_disconnect`, and `mud_status` preserve state results. |
| P | Exercise representative perception, movement, combat, communication, inventory, magic, and utility tools; separately cover the complete registration inventory. |
| Q | Disconnected gameplay returns the exact guard result. |
| R | Ordinary commands drain stale input and read through the prompt sentinel. |
| S | `send_raw` uses the distinct quiet-read path. |
| T | REPL MUD status does not cause a second login. |

### Credentials/provider tests

OpenAI regression tests requiring API access must be separate from offline
tests. MUD tests requiring credentials must likewise be separate and must not
be substituted with provider tests.

## 15. Known evidence gaps and non-goals

- Ruby pre-week `mud_manager` is present locally and is the complete behavioral
  reference, but its internal implementation is Ruby-specific.
- No external Python `mud_manager` dependency exists; the Python `.agents`
  helper is a protocol/login reference, not a production dependency.
- Existing-session yes/no reconnect behavior is instructor-observed and is not
  fully encoded in Step 10 source; only source-supported already-connected
  behavior is required.
- Neither Ruby iteration contains tests.
- The README/demo filename inconsistency remains an evidence note.
- No architectural redesign is authorized.
- No higher-level filesystem traversal abstraction is authorized.
- No shell-security redesign beyond Step 10's first-token allow-list is
  authorized.
- No provider, Docker, MUD, REPL, or application runtime is part of plan
  creation.
- No generated artifact cleanup is part of the work.

## 16. Implementation stop conditions

During future implementation, stop and report instead of improvising if:

- Ruby-observable Session semantics cannot be reproduced;
- Python helper behavior conflicts materially with the Ruby reference;
- prompt/read buffering cannot be made deterministic enough to satisfy the
  required contracts;
- implementing the boundary would require broad architecture outside the
  bounded Session/Primitives compatibility layer;
- Python Step 9's actual architecture differs materially from this plan;
- a proposed change would require redesigning Agent, Registry, providers, or
  the package-resource mechanism;
- tests reveal behavior inconsistent with Ruby Step 10 and the discrepancy
  cannot be explained by a language-level implementation detail;
- prompt-sentinel, stale-input, login, or shared-session semantics cannot be
  implemented faithfully;
- fixing a discovered issue would expand scope beyond Step 10;
- live tests expose behavior that cannot be reconciled with source evidence;
- a required external credential, MUD server, or provider runtime is absent.

At a stop condition, preserve the historical Step 9 iteration and report the
evidence and decision needed from the user. The absence of a third-party
Python `mud_manager` is not, by itself, a stop condition.

## 17. Plan status

- Phase 1 Ruby semantic delta: passed.
- Phase 2 initial Python plan: passed.
- Phase 2B repository archaeology: passed.
- The MUD dependency evidence gap is resolved into a bounded
  Session/Primitives compatibility-port decision.
- This plan is ready for final review before implementation authorization.
