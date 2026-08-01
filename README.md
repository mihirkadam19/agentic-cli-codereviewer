# codechk

AI-powered code review CLI, built around a `ReviewAgent` abstraction so
more specialized reviewers can be added without reworking the pipeline.

## Setup

```bash
pip install -e . --break-system-packages
export ANTHROPIC_API_KEY=sk-ant-your-key
```

## Usage

```bash
# from inside a git repo, with some uncommitted changes
codechk review
```

## Architecture

```
app/
  cli.py                  # entry point, agent registry
  schema.py               # Diff, Context, Finding -- the shared contract
  orchestrator.py         # fans out to agents, merges findings
  llmClient.py            # the only module that talks to the model API
  config.py               # loads .yourtool.toml
  agents/
    baseAgent.py          # ReviewAgent interface
    performanceAgent.py   # v1 preformance reviewer
    securityAgent.py      # v1 security reviewer
    styleAgent.py         # v1 style reviewer
  diff/extractor.py       # git diff -> Diff
  context/builder.py      # Diff -> Context
  output/terminal.py      # Finding list -> terminal output
```



## Config

Create `.chodechk.toml` in a repo you want to review:

```toml
model = "claude-sonnet-4-6"
agents = ["<agent-1>", "<agent-2>"]
```
