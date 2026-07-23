# Claude Code Camp 2026 Q2

## Project Scenario

This repository documents my work through the Claude Code Camp 2026 Q2.

The overall objective is to investigate autonomous software agents by having
an LLM interact with a traditional CircleMUD (tbaMUD) environment as if it
were a human player.

Rather than scripting every action, the goal is to determine how much of the
agent's behavior can emerge from observation, reasoning, and iterative
exploration while keeping deterministic software responsible only for
communication, safety, and protocol management.

The long-term objective is to build a Player Journey Agent capable of:

- exploring an unfamiliar world;
- building an internal map;
- identifying player friction points;
- reasoning about navigation;
- documenting discoveries;
- eventually evaluating the new-player experience.

CircleMUD serves as the experimental environment before introducing larger
agent workflows or proprietary systems.

---

# Engineering Philosophy

One of the primary goals of this repository is to investigate the proper
division of responsibilities between deterministic software and a language
model.

Throughout these experiments the following architecture emerged.

**The language model should own:**

- observation;
- reasoning;
- hypothesis formation;
- planning;
- decision making;
- world-model construction;
- reporting.

**Deterministic software should own:**

- TCP/Telnet communication;
- authentication;
- protocol handling;
- command validation;
- timeout detection;
- safety enforcement;
- clean logout.

Keeping these responsibilities separate allows the helper software to remain
small, deterministic, testable, and reusable while preserving the autonomy of
the agent.

---

# Agent Skills

This project makes extensive use of **Codex CLI project-local Skills**.

Per the current Codex CLI methodology, project-local skills are discovered
from the repository root using the following structure:

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

The `.agents` directory is intentionally located at the repository root so
that Codex CLI can automatically discover project-local skills and their
associated helper scripts.

Each skill contains:

- a `SKILL.md` file describing the agent's mission, constraints, and expected
  behavior;
- optional helper scripts that implement deterministic functionality required
  by the skill.

Current skills include:

### mud-login

Provides deterministic login to tbaMUD.

Responsibilities include:

- authentication;
- session startup;
- entering the game;
- reliable communication;
- clean logout.

The skill does **not** decide where the agent should go.

---

### mud-explore

Provides the framework for autonomous exploration.

The language model remains responsible for:

- selecting commands;
- interpreting room descriptions;
- forming hypotheses;
- ranking alternative routes;
- building an internal world model;
- determining when the objective has been achieved.

The helper transports commands and enforces safety constraints.

It does **not** contain navigation logic or hard-coded routes.

---

# Repository Layout

```text
week0_explore/
│
├── explore_architecture/
│   ├── 01_plain_agent/
│   └── 02_agent_skills/
│
├── infrastructure/
│
├── mud_manager/
│
└── ...
```

The exploration architecture directories document the evolution of the agent.

## 01_plain_agent

Documents the earliest experiments, including:

- deterministic login;
- room inspection;
- command discovery;
- communication challenges;
- initial world observations.

## 02_agent_skills

Documents the transition from a simple login helper to autonomous
exploration.

Topics include:

- project-local Skills;
- deterministic helper design;
- evidence-based navigation;
- persistent world knowledge;
- semantic reasoning;
- successful autonomous bakery discovery.

---

# Current Architecture

```text
               Codex CLI
                    │
        reasoning / planning
                    │
                    ▼
            Project-local Skill
                    │
             mission definition
                    │
                    ▼
           Deterministic Helper
                    │
       TCP / Telnet communication
                    │
                    ▼
                 tbaMUD
```

The intelligence lives in the language model.

The helper simply makes reliable interaction possible.

---

# Current Progress

The repository currently demonstrates:

- deterministic authentication;
- safe command execution;
- project-local Skill discovery;
- autonomous room-by-room exploration;
- evidence-based navigation;
- hypothesis-driven search;
- semantic reasoning from room names and landmarks;
- successful autonomous discovery of **The Bakery** without hard-coded
  navigation.

The bakery experiment represents an important milestone because the route was
not encoded in software. The agent developed and refined hypotheses based on
observations gathered during exploration and terminated only after obtaining
direct environmental evidence that the objective had been reached.

---

# Future Work

Upcoming areas of investigation include:

- expanding the agent's internal world model;
- improving navigation efficiency;
- evaluating route planning;
- introducing controlled NPC interaction;
- studying information gathering through dialogue;
- mapping larger regions of the MUD;
- comparing different frontier and local language models on identical
  autonomous tasks.

---

# Acknowledgements

This repository documents an ongoing engineering investigation into autonomous
software agents.

The emphasis is not simply on reaching destinations within the MUD, but on
understanding **how** an agent learns, reasons, and improves through
observation while deterministic software provides only the reliable mechanics
of communication.