Player Knowledge

Experiment Context

This file documents the behavior of Codex CLI during the 02_agent_skillsphase of the tbaMUD exploration architecture.

The objective was to determine whether Codex could locate The Bakerywithout being given a hard-coded route.

Codex used:

the project-local mud-explore skill;

the deterministic Python exploration helper;

room descriptions;

visible exits;

landmarks;

prior observations retained during the session;

hypothesis-driven navigation.

The helper transported one validated command at a time. It did not containthe bakery route or make navigation decisions.

Character

Name: UltraMan

Starting location for this experiment: The Eastern End Of The Alley

Goal: Locate The Bakery

Movement budget: 50 commands

Movements required: 12

Result

Codex successfully located the bakery.

Success was based on direct evidence:

the room was explicitly named The Bakery;

the description referenced danish and fine bread;

shelves and a baker were visible.

Codex did not claim success through inference alone.

Autonomous Reasoning Behavior

No hard-coded route

The route was not stored in:

SKILL.md;

explore.py;

login.py;

the mission prompt.

The prompt defined the goal, constraints, and reasoning process, but not thedirections needed to reach the destination.

Codex selected each command after interpreting the most recent game output.

Persistent session knowledge

Codex treated confirmed observations as persistent knowledge for theremainder of the run.

It retained information about:

previously visited rooms;

discovered exits;

commercial districts;

dead ends;

known route segments;

landmarks that appeared relevant to the search.

This reduced unnecessary rediscovery and allowed later decisions to build onearlier observations.

Hypothesis-driven exploration

Codex did not treat every unexplored direction as equally valuable.

It formed the hypothesis that a bakery was more likely to be found near:

Market Square;

Main Street;

shops;

commercial branches;

named merchant locations.

It used semantic relationships between the objective and the environment:

bakery
→ food and commerce
→ market or shop district
→ Main Street branches

This improved the search compared with the earlier 20-movement experiment,which spent more time in alleys, the dump, the levee, and warehouse areas.

Route ranking

When multiple routes were available, Codex ranked them by expected relevance.

Commercially named routes were preferred over:

isolated alleys;

dumps;

city edges;

warehouse areas;

branches with no bakery-related evidence.

This changed the search from broad wandering into targeted investigation.

Evidence-based command selection

Codex used informational commands when they could reduce uncertainty.

Observed examples included:

look;

exits;

look note in the General Store.

The look note command is especially important because it shows that Codexnoticed an environmental object and investigated whether it might containuseful information.

Backtracking and recovery

Codex revisited known rooms only when:

returning from an unpromising branch;

moving back toward a commercial district;

testing a revised hypothesis.

Backtracking was purposeful rather than accidental.

Bounded autonomy

Codex remained autonomous within explicit safety boundaries.

It did not:

attack;

initiate combat;

speak with NPCs;

purchase or sell items;

alter inventory;

modify the character;

use administrator commands;

modify repository files.

The movement budget remained active, but Codex found the goal after only12 movements.

Verified Route Taken

west
→ west
→ west
→ north
→ east
→ north
→ south
→ east
→ west
→ west
→ west
→ north

This is the route taken during the successful run. It should be treated as anobserved result, not as a route that was supplied to Codex beforehand.

Agent Capability Demonstrated

This experiment demonstrated that Codex can:

maintain an internal world model across repeated helper invocations;

reason from room names and semantic clues;

rank competing navigation options;

revise hypotheses when evidence changes;

recover from less promising branches;

preserve safety constraints;

stop only when direct evidence satisfies the goal.

Architectural Finding

The successful bakery search reinforces the separation of responsibilities:

Codex

observes;

reasons;

forms hypotheses;

ranks routes;

selects commands;

remembers discoveries;

updates its world model;

determines when success has been proven.

mud-explore skill

defines the mission;

establishes safety constraints;

requires evidence-based reporting;

encourages persistent knowledge and route ranking.

Python helper

authenticates;

manages TCP/Telnet communication;

validates commands;

sends one selected command;

returns output;

logs out safely.

The Python helper remained deterministic and did not contain agentintelligence.

Comparison With the Previous Bakery Attempt

Previous attempt

movement limit: 20;

result: bakery not found;

exploration included alleys, the dump, the levee, warehouses, and city-edgeareas;

reasoning was safe, but the search covered too many low-probability routes.

Successful attempt

movement limit: 50;

result: bakery found after 12 movements;

persistent knowledge was emphasized;

alternative routes were ranked;

commercial districts were prioritized;

confirmed information was reused;

semantic reasoning guided navigation.

The improvement came primarily from a better reasoning strategy, not fromhard-coding the destination.

Remaining Questions

Can Codex navigate from The Bakery back to the Temple using its accumulatedmap?

Can it reproduce the route in a fresh session using only journaled worldknowledge?

Can it find another commercial landmark with the same strategy?

Can it distinguish between replaying a known route and planning from aworld model?

How should controlled NPC dialogue be introduced in a later phase?