# Installation and first use

Install all five skills together. `learn-next`, `learn-progress`, `learn-test`, and `learn-review` use resources in their sibling `learn-start` directory. Installing just one of them leaves the bundle incomplete.

Choose one installation method for a destination. The Python installer manages its own manifest; `npx skills` manages its own links and lock files. Use the same tool for later updates and removal.

## Quick installation from GitHub

With Node.js 22.20+ and Git available, use the third-party [Skills CLI](https://github.com/vercel-labs/skills). For example, install the whole bundle for Codex across projects:

```sh
npx skills add JuliossJunk/learn-it-skill --skill '*' --agent codex --global
```

Replace `codex` with `claude-code`, `cursor`, `github-copilot`, or `opencode`. Multiple agent IDs can follow `--agent`. Keep `--skill '*'` to select the entire bundle. The command is interactive so you can review the target paths. Add `--copy` if you prefer copies or cannot create symlinks.

For project scope, run from the intended project's directory and omit `--global`. The CLI chooses its own supported paths, which may use `.agents/skills` for several agents. Inspect existing same-name skills before accepting replacement.

```sh
npx skills add JuliossJunk/learn-it-skill --list
npx skills list --global
npx skills check
npx skills update learn-start learn-progress learn-next learn-test learn-review --global
npx skills remove --global learn-start learn-progress learn-next learn-test learn-review
```

The CLI's [installation and lifecycle reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) describes its prompts, scope, updates, and removal. These commands apply to installations made with that CLI.

## Bundled Python installer

This method needs Python 3.10+ and a clone or [downloaded ZIP](https://github.com/JuliossJunk/learn-it-skill/archive/refs/heads/main.zip) of this repository. Extract the ZIP first. It uses the standard library, makes regular copies, and performs no network requests during installation. Windows, macOS, and Linux use the same commands. If your system names Python `python3`, substitute that for `python`; on Windows, `py -3` is another option.

```sh
git clone https://github.com/JuliossJunk/learn-it-skill.git
cd learn-it-skill
python scripts/install.py install --agent codex
python scripts/install.py check --agent codex
```

The default is user scope. Select one of the five supported agents with `--agent`. These are the bundled installer's destinations, checked against the linked vendor documentation:

| Agent ID | User scope | Project scope | Documentation |
| --- | --- | --- | --- |
| `codex` | `~/.agents/skills/` | `.agents/skills/` | [OpenAI](https://learn.chatgpt.com/docs/build-skills) |
| `claude-code` | `~/.claude/skills/` | `.claude/skills/` | [Claude Code](https://code.claude.com/docs/en/skills) |
| `cursor` | `~/.cursor/skills/` | `.cursor/skills/` | [Cursor](https://cursor.com/help/customization/skills) |
| `github-copilot` | `~/.copilot/skills/` | `.github/skills/` | [GitHub](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |
| `opencode` | `~/.config/opencode/skills/` | `.opencode/skills/` | [OpenCode](https://opencode.ai/docs/skills/) |

`~` means the home directory of the account running Python. Each destination receives the same five sibling skill directories and a `.learn-it-install.json` file containing their hashes. This file belongs to the installer; it is not learning progress. The installer does not change agent settings or grant tool permissions. Some agents also discover other agents' compatibility directories, so an existing installation may already be visible; avoid unnecessary duplicate copies.

Project installation requires an explicit existing project directory:

```sh
python scripts/install.py install --agent opencode --scope project --project /path/to/course
python scripts/install.py check --agent opencode --scope project --project /path/to/course
```

Use a quoted path for spaces, for example `--project "C:\Learning Projects\Probability"`. The project can be a dedicated learning workspace; it does not have to be the clone of this repository. User-level installs are local to that machine. To make skills available to a repository-based remote agent, use project scope and include the installed skill directories in that repository when appropriate. Installed agent applications themselves are outside this installer's scope.

### Preview, update, and remove

```sh
python scripts/install.py install --agent codex --dry-run
git pull --ff-only
python scripts/install.py install --agent codex --update
python scripts/install.py check --agent codex
python scripts/install.py uninstall --agent codex --dry-run
python scripts/install.py uninstall --agent codex
```

Use the same `--scope project --project /path/to/course` options on every command for a project installation. A ZIP download can be updated by downloading a fresh copy and running its installer with `--update` instead of using `git pull`.

- `--dry-run` reports the destination and current file status without creating directories or writing files.
- A repeated current installation leaves files unchanged. An identical manually copied bundle can be adopted by writing the installer's manifest.
- Updates require `--update` and an unchanged managed installation. Modified or conflicting skills block the operation before any installed skill is changed. Compare and preserve local edits first; there is no force-overwrite option.
- A normal filesystem failure during replacement triggers restoration of the previous bundle. Keep backups when managing valuable customizations; abrupt process termination is outside this rollback guarantee.
- Uninstall removes only this installer's unchanged bundle and manifest. It preserves unrelated skills and refuses to remove unmanaged or modified copies. Python cache files do not count as user edits.
- `check` exits with status 0 only when all five managed skills match this checkout. Missing, modified, unmanaged, or outdated files produce status 1. It checks files and shared resources, not the agent application's runtime discovery.
- Linked destination directories, including Windows junctions, are refused. Manage a link-based installation with its original tool, or choose a regular destination.

## Ask a coding agent to install it

Paste this into the coding agent you want to use:

```text
Install the complete Learn It bundle from https://github.com/JuliossJunk/learn-it-skill
for this coding agent at user scope. Read docs/installation.md in that repository.
Reuse a suitable checkout or clone it into an appropriate workspace folder.
Use its bundled Python installer with the agent ID matching this host.
If the host is unclear, ask which agent I use. Inspect a dry run first and
preserve existing skill edits. Install all five skills together, run check,
and tell me the destination and how to start learn-start. Follow the host's
permissions for writes outside the workspace. Do not start a course yet.
```

For a project-only installation, replace “at user scope” with “at project scope in [your project path]”. This prompt requests installation only; course creation starts when you ask for it.

## Start learning

After installation, open your intended course workspace and ask for a learning project. Explicit invocation differs by host:

| Agent | Example |
| --- | --- |
| Codex | `$learn-start I want to learn probability` |
| Claude Code | `/learn-start I want to learn probability` |
| Cursor | `/learn-start I want to learn probability` |
| GitHub Copilot | Ask “Use the learn-start skill to help me learn probability” |
| OpenCode | Ask “Load the learn-start skill and help me learn probability” |

Natural-language requests can also trigger a matching skill. Lessons and reports follow your communication language, regardless of the English installation instructions. For subsequent work, ask to continue, show progress, check understanding, or produce an HTML review. OpenCode loads skills through its native skill tool; the other agents' slash or dollar syntax is not assumed to apply there.

## If a skill does not appear

Run the bundled `check` for a Python-managed installation, or `npx skills list` with the correct scope for a CLI-managed installation. Confirm that the command ran under the same account and on the same machine as the agent. Reload the agent session if newly added skills are not visible; Codex's guide specifically recommends restarting when changes do not appear.

If files are present, inspect the agent's skill list and any workspace trust or skill-access settings. For OpenCode, denied skill permissions or a disabled skill tool can hide a skill. A remote worker needs the files in its own filesystem; a local user installation alone does not put them there. Check that all five siblings exist before investigating a broken shared-contract link.

If PowerShell blocks `npx.ps1` under its execution policy, use `npx.cmd` with the same arguments, or use the bundled Python installer. No execution-policy change is needed for the Python route.
