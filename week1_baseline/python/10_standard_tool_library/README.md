# Step 10 — A Standard Tool Library

Python Step 10 gives the agent a standard library of 34 automatically
registered tools: six filesystem tools, one shell tool, and 27 MUD tools.

## Tool groups

Filesystem tools are `pwd`, `list_directory`, `read_file`, `write_file`,
`delete_file`, and `search_files`. Paths are confined to `working_dir`; paths
that escape the root return an error string.

The shell tool is `run_command`. It runs in `working_dir`, defaults to a
30-second timeout, combines stdout and stderr, reports `(no output)`, annotates
nonzero exits with `[exit N]`, and supports the Ruby-compatible first-token
`allowed_commands` list.

MUD tools cover connection, perception, movement, combat, communication,
inventory/equipment, magic, and utility operations. They share one long-lived
Session. Registration attempts to connect and log in automatically; explicit
`mud_connect`, `mud_disconnect`, and `mud_status` remain available.

## Configuration

`working_dir` defaults to the current directory. Pass `working_dir=False` to
disable filesystem and shell tools. Pass `mud=False` to disable MUD tools.
MUD options may be supplied explicitly or resolved from the configured
`settings.yaml` MUD block. The global launcher also supports the legacy
`MUD_NAME`, `MUD_HOST`, `MUD_PORT`, and `MUD_PASSWORD` environment variables.

The MUD compatibility boundary is package-local:

- `boukensha/mud/session.py` — TCP/Telnet session, login, buffering, and reads;
- `boukensha/mud/primitives.py` — stateless builders for the commands used by
  Step 10;
- `boukensha/tools/mud.py` — Registry tool registration.

The implementation is derived from the complete local Ruby pre-week reference
at `week0_explore/mud_manager/` and protocol/login lessons in the local
`.agents` helpers. The `.agents` helpers are not runtime dependencies.

## Demo and prerequisites

The example demonstrates the intended MUD task but is not run by offline
validation. A live MUD server, character credentials, and configured provider
are required for the complete demo. No live behavior is claimed as verified
by this iteration's offline validation.

```sh
python examples/example.py
```

Known limitations are kept faithful to the curriculum: the implementation
does not redesign shell security, add unused MUD primitives, or invent a fix
for the instructor-observed existing-session yes/no edge case that is not
fully encoded in the source reference.
