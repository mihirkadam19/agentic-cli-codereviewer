# codechk

**AI-powered, multi-agent code review — from the command line.**

`codechk` runs specialized LLM reviewers against your local changes or individual files, right from your terminal. Rather than a single general-purpose prompt, review responsibility is split across dedicated agents — each focused on one concern — orchestrated in parallel and merged into a single findings report.

---

## Features

- **Multi-agent review** — dedicated `security`, `performance`, and `style` agents, each with its own prompt and scope, rather than one generalist reviewer trying to do everything at once.
- **Parallel orchestration via LangGraph** — configured agents run concurrently as graph nodes and converge into a single aggregation step, rather than running one after another.
- **Structured output, not parsed prose** — findings are returned through the Anthropic API's tool-use mechanism, validated server-side against a schema, instead of asking the model to emit JSON as text and hoping it complies.
- **Diff-based or file-based review** — review only what changed in your working tree (`codechk review`), or run a focused scan against a single file (`codechk security --file path/to/file.py`).
- **Local response caching** — identical review requests are served from a local disk cache instead of re-querying the model, avoiding repeat cost on unchanged content.
- **Config-driven, not code-driven** — which agents run and which model powers them is controlled by a `.codechk.toml` file per repo, not hardcoded.

---

## Requirements

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)
- Git (for diff-based review)

---

## Installation

```bash
git clone https://github.com/mihirkadam19/agentic-cli-codereviewer.git
cd agentic-cli-codereviewer
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-your-key
```

> On Debian/Ubuntu systems with an externally-managed Python environment, add `--break-system-packages` to the `pip install` command, or install inside a virtual environment instead.

---

## Usage

### Review local changes

Reviews everything currently changed but not yet committed, using every agent configured in `.codechk.toml` (or the defaults, if no config file is present):

```bash
codechk review
```

Diff against a specific ref instead of `HEAD`:

```bash
codechk review --against main
```

### Run a single agent against one file

For a focused, single-concern scan of one file, independent of git state:

```bash
codechk security --file app/auth.py
codechk performance --file app/queries.py
```

### Example output

```
app/auth.py
  [!] (security) line 42: User-supplied input passed directly into SQL query
      -> Use parameterized queries instead of string interpolation
  [i] (style) general: Function is missing a docstring
```

---

## Configuration

Create a `.codechk.toml` file in the root of the repository you want to review:

```toml
model = "claude-sonnet-4-6"
agents = ["security", "performance", "style"]
```

| Key      | Description                                              | Default                                     |
|----------|------------------------------------------------------------|----------------------------------------------|
| `model`  | Anthropic model used for all agents                        | `claude-sonnet-4-6`                          |
| `agents` | Which agents run during `codechk review`                    | `["security", "performance", "style"]`       |

If no `.codechk.toml` is present, these defaults are used automatically — no configuration is required to get started.

---

## Architecture

```
app/
├── cli.py                   # Entry point; agent registry; command definitions
├── schema.py                 # Shared data models: Diff, Context, Finding
├── orchestrator.py           # LangGraph orchestration: fan-out to agents, aggregate results
├── llmClient.py              # Sole interface to the Anthropic API (model calls, tool use, caching)
├── cache.py                  # Disk-based cache for LLM responses, keyed by prompt content
├── config.py                 # Loads .codechk.toml, falls back to defaults
├── agents/
│   ├── baseAgent.py          # Shared review flow: prompt assembly, LLM call, Finding construction
│   ├── securityAgent.py      # Security-focused reviewer
│   ├── performanceAgent.py   # Performance-focused reviewer
│   └── styleAgent.py         # Style and readability-focused reviewer
├── diff/
│   └── extractor.py          # Extracts a normalized Diff from `git diff`
├── context/
│   └── builder.py            # Gathers surrounding file content for a diff or single file
└── output/
    └── terminal.py           # Renders findings to the terminal
```

### Review flow

1. **Extraction** — `diff/extractor.py` reads `git diff`, or `--file` points directly at a single file.
2. **Context** — `context/builder.py` pulls in the relevant file content surrounding the change.
3. **Orchestration** — `orchestrator.py` builds a LangGraph graph: every configured agent runs as a parallel node fed from a shared start state, converging into a single `aggregate` node that de-duplicates overlapping findings.
4. **Agent review** — each agent (`BaseAgent` subclass) builds its own prompt and calls the model via `llmClient.py`, which returns findings through a forced tool call rather than parsed free text.
5. **Caching** — before any model call, `llmClient.py` checks a local cache keyed on the exact model/system/user prompt; a cache hit skips the API call entirely.
6. **Output** — `output/terminal.py` renders the merged findings, grouped by file.

### Adding a new agent

1. Create `agents/<name>Agent.py`, subclassing `BaseAgent` and supplying a `SYSTEM_PROMPT`.
2. Register it in `_AGENT_REGISTRY` in `cli.py`.
3. Add it to the `agents` list in `.codechk.toml`.

No changes are required to the orchestrator, diff extractor, context builder, or output formatter — every agent communicates through the same `Finding` schema.

---

## Caching

Review responses are cached locally at `~/.codechk/cache/`, keyed by a hash of the exact model, system prompt, and user prompt sent to the API. Running the same review twice with no underlying changes returns the cached result instead of making a new API call. Cache entries do not expire automatically; clear the directory manually to force fresh results.

---

## Roadmap

- Dedicated `style` subcommand (currently only runs as part of `review`)
- `--no-cache` flag to bypass the cache on demand
- Tree-sitter–based context extraction (enclosing function/class instead of full-file content)
- GitHub Action integration for posting findings as inline PR comments
- Automated test suite

---

## License

MIT — see [LICENSE](./LICENSE) for details.