# Preweek Technical Documentation

## Technical Goal

The technical goal of Preweek was to determine whether Codex CLI Luna, running at the lowest reasoning setting, could operate a traditional text-based MUD as an autonomous player agent.

The larger business use-case for me is personal AI developmental understanding with how to create a Player Journey Agent capable of playing the MUD like a real user. The agent should be able to explore the world, remember where it has been, locate important destinations, and identify areas where a player may become confused, blocked, bored, lost, or overpowered by others non playable characters such as Minotaurs.

During Preweek, the immediate technical goals were smaller and more focused:

- determine whether Codex CLI could connect to tbaMUD;
- determine whether it could authenticate as the player `UltraMan`;
- determine whether it could interact with the MUD through its text-command interface;
- investigate whether a project-local Codex Skill could provide reusable instructions;
- separate the agent's reasoning from the low-level Telnet communication;
- allow Codex to discover available commands and movement behavior;
- determine whether Codex could navigate without being given a hard-coded route;
- create simple Markdown memory files for player and world knowledge;
- document the technical challenges and architectural decisions discovered during the experiments.

The primary architectural question was:

> Can Codex CLI remain responsible for observation, reasoning, and navigation while deterministic helper software manages only the connection, authentication, command transmission, safety limits, and logout?

---

## Technical Uncertainty

At the beginning of Preweek, I was uncertain whether a coding harness designed mainly for software-development tasks could effectively operate a non-coding workload such as a live text-based MUD.

The MUD does not expose a conventional REST API. Instead, the agent must interact through a long-lived TCP/Telnet session containing prompts, menus, room descriptions, movement commands, paginated help output, and changing session states.

My main technical uncertainties were:

- whether Codex CLI could maintain a persistent interactive Telnet session;
- whether standard tools such as `nc localhost 4000` would work reliably inside the Codex command runner;
- whether Codex could recognize login prompts and character-menu states;
- whether the model could remember previous room observations across multiple command executions;
- whether a generic Codex Skill would be sufficient or whether specialized helper code would be required;
- whether Codex could discover MUD commands through `help`, `commands`, and environmental output;
- whether Codex could navigate by reasoning from room descriptions rather than following directions supplied in the prompt;
- whether simple Markdown files such as `player.md` and `world.md` could act as practical memory for the agent;
- whether the lowest reasoning setting would be sufficient for route planning and evidence-based exploration;
- whether strict safety constraints would prevent the agent from entering combat, purchasing items, modifying the character, or becoming trapped in a loop.

I initially believed that Codex might require a completely specialized agentic loop before it could perform useful MUD navigation.

I also suspected that managing the Telnet session would be the primary technical sticking point.

That hypothesis was mostly correct, but the experiments also showed that we did not need to place navigation intelligence inside the helper. We needed a reliable interface between Codex and the MUD.

---

## Technical Observation

The first major observation was that Codex CLI could verify that the tbaMUD server was reachable, but it could not reliably maintain the required interactive session using:

```bash
nc localhost 4000
```

The connection required a sequence of changing prompts:

1. wait for the character-name prompt;
2. send `UltraMan`;
3. wait for the password prompt;
4. send the password which is stored as an environment variable;
5. press Return;
6. receive the character menu;
7. select option `1`;
8. wait for the in-game prompt;
9. issue a command;
10. capture the response;
11. log out safely.

Codex could produce shell commands and scripts, but the command runner did not provide a reliable persistent terminal interaction using `nc`.

I investigated several possible terminal and pseudo-terminal approaches. The results showed that the problem was not whether Codex understood the required actions. The problem was maintaining the low-level prompt-response connection.

A deterministic Python helper was therefore created to manage:

- TCP/Telnet communication;
- authentication;
- prompt detection;
- command transmission;
- timeouts;
- pager handling;
- safe logout.

The helper reads the password from the `MUD_PASSWORD` environment variable. The password is not written into the repository, logs, prompts, or Markdown journal files.

Another important observation was that project-local Codex Skills are discovered from the repository-root structure:

```text
.agents
└── skills
    ├── mud-explore
    │   ├── SKILL.md
    │   └── scripts
    └── mud-login
        ├── SKILL.md
        └── scripts
```

The `.agents` directory must remain at the root of the repository so Codex CLI can discover the `SKILL.md` files and their helper scripts.

The `mud-login` skill established deterministic authentication.

The `mud-explore` skill established the exploration policy and separation of responsibilities.

The most useful interface became:

```bash
python3 .agents/skills/mud-explore/scripts/explore.py --command "<command>"
```

Each execution:

1. logs in as UltraMan;
2. enters the game;
3. sends exactly one validated command selected by Codex;
4. prints the returned MUD output;
5. logs out safely.

The Python helper does not know where the bakery, Newbie Zone, shops, or other landmarks are located.

It contains no navigation route.

Codex remains responsible for deciding which command to send.

During command discovery, Codex successfully tested commands including:

- `look`;
- `help`;
- `commands`;
- `exits`;
- `score`;
- `west`;
- `east`.

The `help` command revealed another technical challenge. The output was paginated and waited for a prompt similar to:

```text
[Return to continue, (q)uit, (r)efresh, (b)lock, or page number]
```

The initial helper timed out because it expected the normal MUD prompt.

Pager handling was then added to the helper.

The first combat detector also produced a false positive because the word `combat` appeared in the help documentation. The detector was updated to identify actual combat-state phrases rather than classifying every mention of the word `combat` as an active fight.

The exploration helper uses a command allowlist and forbidden-command categories. It permits informational commands and basic movement while rejecting command families related to:

- combat;
- administrator access;
- purchasing and selling;
- inventory changes;
- object changes;
- character modification.

The first bakery search was limited to 20 movement commands. Codex explored several rooms, maintained a route, intentionally backtracked from dead ends, respected the movement limit, and honestly reported that the bakery was not found.

The second bakery experiment changed the reasoning strategy.

Codex was instructed to:

- treat confirmed observations as persistent knowledge;
- avoid rediscovering information unnecessarily;
- rank competing routes;
- prioritize commercial districts;
- form and revise hypotheses;
- require direct evidence before declaring success.

Using this strategy, Codex located **The Bakery** in 12 movement commands.

The success was not based on inference alone. The room was explicitly named `The Bakery`, and the description included danish, fine bread, shelves, and a baker.

This was important because the improvement came from better reasoning, not from changing the helper or hard-coding the route.

Codex used semantic reasoning similar to:

```text
bakery
→ food and commerce
→ market area
→ Main Street
→ western commercial branch
```

Codex also discovered and used a note in the General Store with:

```text
look note
```

This demonstrated that it could notice an environmental object and investigate whether it contained useful information.

Additional world knowledge included:

- Temple Of Midgaard;
- Temple Square;
- Common Square;
- Market Square;
- Main Street;
- General Store;
- Pet Shop;
- Weapon Shop;
- Armory;
- Guild of Swordsmen;
- alleys;
- levee;
- warehouses;
- The Bakery.

Codex remained within the safety constraints. It did not attack, purchase, sell, alter inventory, modify the character, use administrator commands, or interact with NPCs.

The following navigation route was also confirmed during the exploration work:

```sh
To reach the **Newbie Zone** from Market Square:
1. `north` → Temple Square
2. `north` → Temple
3. `north` → Altar
4. `north` → Behind Altar
5. `north` → Great Field
6. `north` → Great Field (with newbie zone sign)
7. `east` → Newbie Zone entrance
8. `north` → Enter corridor
```

The Preweek experiments demonstrated an important distinction:

> The helper should know how to communicate with the MUD, but it should not know how to play the MUD.

Codex should remain responsible for observing, reasoning, planning, selecting commands, and updating its world model.

---

## Technical Conclusion

Codex CLI Luna, operating at the lowest reasoning setting, is capable of driving the tbaMUD when it is provided with a deterministic interface for the Telnet session.

A plain instruction file alone was not enough to manage the connection reliably.

However, a Codex Skill combined with a small helper script was sufficient to provide:

- reliable login;
- prompt handling;
- safe command execution;
- paginated output handling;
- movement;
- room observation;
- controlled logout.

The experiments did not support the idea that all MUD intelligence needed to be placed inside a custom Python loop.

Instead, the most successful architecture separated the system into three layers:

### Codex CLI

Responsible for:

- observation;
- reasoning;
- hypothesis formation;
- planning;
- command selection;
- world-model construction;
- reporting.

### `SKILL.md`

Responsible for:

- defining the task;
- setting behavioral constraints;
- explaining the helper interface;
- defining safety boundaries;
- defining the expected report.

### Python helper

Responsible for:

- TCP/Telnet communication;
- authentication;
- prompt recognition;
- command validation;
- output capture;
- timeout handling;
- clean logout.

The bakery experiment demonstrated that Codex could improve its navigation through prompt-guided reasoning without receiving a hard-coded route.

The first attempt used 20 movements and did not locate the bakery.

The second attempt reused accumulated knowledge, ranked routes, prioritized commercial districts, and located the bakery in 12 movements.

This shows that the quality of the reasoning strategy mattered more than simply increasing the movement budget.

Simple Markdown memory files were useful for documenting player capabilities and world knowledge. However, long-term navigation will probably require a more structured world representation than free-form notes alone.

The remaining technical uncertainty is not whether Codex can operate the MUD.
It can.

The remaining uncertainty is how to scale this architecture for:

- longer sessions;
- larger maps;
- multiple goals;
- persistent memory;
- controlled NPC conversations;
- multiple players;
- repeated journey analysis;
- identifying player friction over time.

---

## Key Takeaway

The major Preweek takeaway is that a specialized use-case does not necessarily require placing all of the intelligence architecture inside "SKILL.md" files, or SDKs.

It does require specialized tooling at the boundary where the language model interacts with the external system.

For this MUD experiment:

- Codex provides the intelligence;
- the Skill provides the operating policy;
- the Python helper provides the reliable interface;
- Markdown files provide early-stage player and world memory.

The strongest architecture was not a completely generic agent and not a completely hard-coded agent.

It was a bounded autonomous agent.

Codex was free to observe, reason, form hypotheses, choose commands, backtrack, and improve its search. At the same time, deterministic code handled the fragile Telnet protocol and prevented unsafe commands.

The bakery experiment provided the clearest proof.

Codex found the destination without being given the route and without placing navigation logic inside Python.

The final lesson from Preweek is:

> Keep the intelligence in the agent, but place reliability and safety in deterministic tooling.