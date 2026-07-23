Player Knowledge

Character

Name: UltraMan

Current level: 1

Class: Swordmonger

Observed status: 20 HP, 100 mana, approximately 83–84 movement points

Gold: 0

Quests: None observed

Authentication

UltraMan successfully authenticates through the deterministic Python helper.

The helper reads the password from the MUD_PASSWORD environment variable. The password is not printed, logged, or written to Markdown files.

Verified Login Flow

The following sequence has been validated repeatedly:

Connect to localhost:4000.

Wait for the character-name prompt.

Send UltraMan.

Wait for the password prompt.

Send the password.

Press Return when prompted.

Receive the character menu.

Select option 1 to enter the game.

Wait for the in-game prompt.

Send one approved command.

Capture the response.

Log out cleanly.

Skills and Helpers

Two project-local Codex skills are now relevant:

mud-login provides deterministic staged login behavior.

mud-explore defines the rules for bounded, agent-directed exploration.

The exploration helper is located at:

.agents/skills/mud-explore/scripts/explore.py

Its command-line interface is:

python3 .agents/skills/mud-explore/scripts/explore.py --command "<command>"

Each invocation:

authenticates as UltraMan;

enters the game;

sends exactly one validated command selected by Codex;

prints the MUD response;

logs out safely.

The helper does not contain a route, destination, or exploration strategy. Codex remains responsible for choosing each command after reasoning from the previous response.

Verified Commands

The following commands have been successfully tested:

look

help

exits

score

commands

west

east

quit

Command behavior learned

look describes the current room, visible exits, objects, and nearby entities.

help opens a paginated help system.

exits lists explicit exit directions and destinations.

score displays character state without modifying the character.

commands displays a broader command list.

west and east perform reversible room-to-room movement.

quit exits the active game session.

No combat, purchasing, selling, inventory-changing, object-changing, or administrator commands have been tested.

Interaction Model

The game behaves as a prompt-driven command interface.

The observed interaction cycle is:

receive a room description or game prompt;

select a textual command;

send the command;

receive the command response;

inspect the updated prompt and environment;

decide what to do next.

The in-game prompt exposes player-state information including:

hit points;

mana;

movement points;

optional status labels.

Engineering Challenges and Solutions

Interactive nc was unreliable

Codex CLI could verify that the MUD port was reachable, but it could not reliably maintain the persistent prompt-response interaction required by:

nc localhost 4000

Solution

A deterministic Python helper was created to own:

TCP/Telnet communication;

prompt detection;

authentication;

command transmission;

timeout handling;

clean logout.

This separated protocol reliability from agent reasoning.

The original login helper was too narrow

The first Python helper supported staged login and one fixed look operation. It did not expose a general command interface for exploration.

Solution

Codex created explore.py, which accepts one model-selected command per invocation. This permits iterative room-by-room reasoning without hard-coding navigation.

Help output used a pager

The first help attempt timed out because the game displayed a paginated response and waited for:

[Return to continue, (q)uit, (r)efresh, (b)lock, or page number]

The helper initially expected the ordinary game prompt and did not recognize the pager.

Solution

Pager handling was added so the helper can advance through paginated output and collect the complete response.

Combat detection produced a false positive

The initial safety detector interpreted the word combat in the help-page heading or command category as evidence that combat had begun.

Solution

Combat detection was narrowed to actual combat-state phrases rather than generic mentions of the word combat.

Safe command enforcement

The helper uses command categories such as:

read-only informational commands;

basic movement commands;

forbidden commands.

It rejects combat, administrator, purchasing, selling, inventory-changing, object-changing, and character-changing command families.

Architectural Finding

The most important design decision is the separation of responsibilities:

Codex owns observation, reasoning, planning, and command selection.

SKILL.md defines the mission, boundaries, and reporting requirements.

Python owns deterministic communication, validation, safety checks, and logout.

The helper executes commands but does not decide what the agent should do.

Remaining Unknowns

The route to the bakery

Broader navigation beyond the Temple and Reading Room

Map construction and loop detection over multiple rooms

Shop behavior and economy

Inventory and equipment behavior

Quest mechanics

Combat mechanics

Whether a persistent multi-command session is needed later