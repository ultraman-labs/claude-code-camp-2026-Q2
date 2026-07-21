# Explore Agent Architectures

The largest confusion tech professionals have is applying the correct agent solution because many solutions appear to overlap responsibilities.

We will explore multiple agent architecture to determine fit for our agent workload.

## 1. An agent file with referenced files
**e.g.** `AGENT.md`, `@~/docs/*.MD`

The simplest agent is creating an "agent file" and possibly importing other files that are read conditionally when needed.

We should attempt to create an agent file and see if it can connect to the MUD and complete a simple goal:

> e.g. "Find the bakery and list the menu."

We want to use the smallest and least intelligent model and scale up.

### Technical Observations

- The agent struggled to connect to the MUD.
- The agent would attempt to create temporary code files to manage a telnet connection and execute commands.
- The agent did not have enough information about Text User Interface of the MUD to login and see its mistakes.
- The agent would try and read files not relating to the task.
- Increasing the model intelligence to Sonnet 4.6 did not help.

### Technical Conclusions

We could probably write a better prompt or create an artifact that would give the agent full knowledge of the MUD's Text User Interface to successfully login, but since this experience is so fixed, it would be better to have a script that exactly knows how to login so we are not wasting token usage on deterministic user flows.

Coding harnesses tend to go off task and try to write code which we do not need our agent to do.

Coding harnesses, at least at this specific architecture stage, do not appear to be a good fit.

We are justified to build our own MUD SDK to connect to the MUD since clearly the agent wants to manage the connection via script and execute common commands over the port.

If we had an MCP server to our MUD SDK, then maybe we could drive the agent better at this architectural level.

I think due to the complexity of world and player state data, I simply do not think updating Markdown files will be sufficient but we never concluded whether the current agentic loop of the coding harness could handle said task.

> Use coding harnesses for coding, and for specialized agents make your own loop.

## 2. Agent skills driven by main agent eg. ~/skills

A very common way to drive specific functionality is via Agent skills which is an open format for agents adopted by many coding harnesses and agent SDKs.
