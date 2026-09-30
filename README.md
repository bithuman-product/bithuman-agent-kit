# bitHuman agent kit

Connect an AI coding assistant to the bitHuman docs, and give it a skill for adding a bitHuman avatar to an app.

bitHuman has two current models: Essence 2 renders a photoreal person from one portrait; Expression 2 renders any character (people, animals, cartoons) from one portrait.

This repo holds two things:

| Piece | What it does |
|---|---|
| **Docs MCP server** `https://docs.bithuman.ai/docs-mcp` | The bitHuman docs as a remote MCP server (Streamable HTTP) with two read-only tools, `search` and `fetch`. It needs no account and no key. |
| **Skill** [`skills/bithuman-integrate/SKILL.md`](skills/bithuman-integrate/SKILL.md) | Walks an assistant through an integration: pick a path, install, wire speech to frames, handle the API secret, check it works. Every step points to a docs page. |

The docs server only reads public docs pages. It cannot create avatars, start sessions or touch an account, and it never needs your API secret. The skill tells the assistant to read the secret from the environment and never ask for it, print it or commit it.

To drive bitHuman itself (create agents, render videos) from an MCP client, use the CLI's own MCP server instead: https://docs.bithuman.ai/build/mcp.

## Install the docs MCP server

### Claude Code

```bash
claude mcp add --transport http bithuman-docs https://docs.bithuman.ai/docs-mcp
```

Or install this repo as a plugin (docs server + skill in one step):

```bash
/plugin marketplace add <path-or-git-url-of-this-repo>
/plugin install bithuman@bithuman
```

### Claude Desktop and claude.ai

Settings > Connectors > **Add custom connector**, then paste `https://docs.bithuman.ai/docs-mcp`. No authentication.

### Cursor

Add to `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project); see [`examples/mcp/cursor.mcp.json`](examples/mcp/cursor.mcp.json):

```json
{ "mcpServers": { "bithuman-docs": { "url": "https://docs.bithuman.ai/docs-mcp" } } }
```

### VS Code

Add to `.vscode/mcp.json` in the workspace; see [`examples/mcp/vscode.mcp.json`](examples/mcp/vscode.mcp.json):

```json
{ "servers": { "bithuman-docs": { "type": "http", "url": "https://docs.bithuman.ai/docs-mcp" } } }
```

### ChatGPT

Settings > Apps & Connectors > Advanced settings: turn on **Developer mode**, then **Create** a connector with the URL `https://docs.bithuman.ai/docs-mcp` and no authentication. (Menu names can change; the ChatGPT help pages on custom MCP connectors have the current path.)

### Codex CLI

Append [`examples/mcp/codex.config.toml`](examples/mcp/codex.config.toml) to `~/.codex/config.toml`.

### Any other client

Any client that speaks remote MCP over Streamable HTTP can use [`examples/mcp/generic.mcp.json`](examples/mcp/generic.mcp.json).

## Install the skill

The same skill is published at https://docs.bithuman.ai/skills/bithuman-integrate/SKILL.md. For Claude Code, save it in a project (or in `~/.claude/skills/` for every project):

```bash
mkdir -p .claude/skills/bithuman-integrate
cp skills/bithuman-integrate/SKILL.md .claude/skills/bithuman-integrate/SKILL.md
```

Other assistants: add the file's text to the project's agent instructions.

## Try it

- "Add a talking avatar to my LiveKit voice agent."
- "Put an animated character in my iPhone app."
- "Render an avatar in a browser tab with WebGPU."
- "Which bitHuman SDK fits my project?"

Each answer should cite a docs.bithuman.ai page. Sample avatars you can try without an account: Essence 2 `sofia-ramirez` and Expression 2 `wise-pup`. From 2026-10-12, API and SDK use requires the Creator plan or higher; get an API secret at https://docs.bithuman.ai/start/api-secret.

## Repo layout

| Path | Purpose |
|---|---|
| `skills/bithuman-integrate/SKILL.md` | the skill |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.mcp.json` | Claude Code plugin and marketplace |
| `plugin.json`, `mcp.json`, `assets/` | the plugin bundle for the ChatGPT and Codex plugin directory |
| `examples/mcp/` | per-client MCP configs |
| `scripts/check.py` | local gate: parses every JSON/TOML/YAML file, checks the skill front matter and manifest paths, scans for secrets and, given the claims register, for forbidden wording |

Run the gate (Python 3.11+):

```bash
python3 scripts/check.py                       # parse + structure + secret scan
python3 scripts/check.py --claims <path-to>/truth-register.yaml   # also the claims scan
```

## Links

- Docs: https://docs.bithuman.ai (index: https://docs.bithuman.ai/llms.txt)
- Agents and MCP: https://docs.bithuman.ai/resources/agents
- Support: https://www.bithuman.ai/support
- Privacy: https://www.bithuman.ai/legal/privacy

## License

Apache-2.0. See [LICENSE](LICENSE).
