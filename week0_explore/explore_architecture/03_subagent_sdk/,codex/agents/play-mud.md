---
name: mud-explore
description: Explore the tbaMUD world by reasoning from observations while using a deterministic helper for connection management.
---

# mud-explore

## Purpose

Use this skill when the objective requires exploring the tbaMUD world rather than simply verifying login.

Unlike the `mud-login` skill, this skill is intended for agentic exploration. The language model should determine which commands to issue based on the information it observes during the session.

The helper owns communication.

The language model owns observation, reasoning, planning, and decision making.

---

# Responsibilities

## Language Model

The language model is responsible for:

- observing room descriptions
- interpreting command responses
- reasoning about possible actions
- selecting movement and informational commands
- recognizing landmarks
- building an internal understanding of the world
- explaining its reasoning
- stopping when uncertainty becomes too high rather than hallucinating

## Helper

The helper is responsible for:

- authenticating with the MUD
- managing the TCP/Telnet connection
- transmitting model-selected commands
- capturing command output
- enforcing safety limits
- logging out cleanly
- terminating the session if an unexpected protocol state occurs

The helper intentionally does **not** decide where to move or which commands should be executed.

---

# Safety

Unless explicitly instructed otherwise:

- Do not attack.
- Do not initiate combat.
- Do not purchase or sell items.
- Do not pick up, drop, or modify objects.
- Do not modify the character.
- Do not use administrator commands.

If combat begins unexpectedly:

- Stop the exploration.
- Report what happened.
- Exit the session safely.

---

# Exploration Strategy

Approach exploration as an evidence-driven investigation.

For each step:

1. Observe the current room.
2. Read the room description carefully.
3. Identify visible exits.
4. Consider available evidence.
5. Select the next command.
6. Explain why that command was chosen.
7. Observe the result.
8. Repeat.

Avoid wandering randomly.

Prefer decisions supported by observations.

If insufficient evidence exists, explain the uncertainty instead of guessing.

---

# Reporting

Unless instructed otherwise, report:

- commands issued
- reasoning behind each command
- rooms visited
- exits discovered
- landmarks observed
- navigation decisions
- uncertainty encountered
- final conclusions

---

# Design Philosophy

This skill intentionally separates deterministic communication from agent reasoning.

The helper manages the mechanics of interacting with the MUD, including authentication, session management, reliable command transmission, and safety enforcement.

The language model remains responsible for observing the environment, forming hypotheses, selecting commands, interpreting results, and deciding how to proceed.

This separation keeps the helper deterministic and reusable while preserving the autonomy of the agent.

---

# Current Status

This skill is experimental.

The goal is not to hard-code navigation through the game world.

Instead, the objective is to investigate whether a language model can construct its own understanding of the environment through observation, reasoning, and iterative exploration while relying on deterministic software only for reliable communication.