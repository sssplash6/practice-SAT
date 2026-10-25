# Claude Code "mods": what they are and whether they matter here

Researched 2026-10-04. Notes file only, no app code touched.

Source post: https://claude.dev/blog/getting-started-with-claude-code-mods/ (the pasted link was the same URL twice, concatenated; the single URL loads fine). Title "Getting Started with Claude Code Mods", author Addy Osmani, published 2026-10-01. The post text was fetched through a summarising fetch tool, so quotes below are as that tool returned them, not byte-exact.

First-party sources used (all fetched 2026-10-04):

- [P] Plugins overview: https://code.claude.com/docs/en/plugins
- [H] Hooks reference: https://code.claude.com/docs/en/hooks
- [MO] Mods overview: https://code.claude.com/docs/en/plugins/mods/overview
- [MC] Create a mod: https://code.claude.com/docs/en/plugins/mods/create
- [ME] React to events: https://code.claude.com/docs/en/plugins/mods/events
- [MR] Mods reference: https://code.claude.com/docs/en/plugins/mods/reference
- [MEM] Memory: https://code.claude.com/docs/en/memory
- [GH] https://github.com/anthropics/claude-code and its `mods/` directory (the post links only to the repo root)

## 1. What the post says

- A mod is a small JS/TS file inside a plugin that registers hooks, and each hook "sees every event in your session as it happens". Works in the terminal and the desktop app.
- Hook shape: `on("tool.call", { tool: "Bash" }, async ($, e, next) => ...)`. `$` is the mods API, `e` the event, `next` passes it on. A hook can observe, rewrite, or answer (return without calling `next`).
- Tutorial mod "token-weather": a context-window forecast band above the prompt (sun/cloud/showers/storm by percent used). Quick path: just ask Claude Code to write it; hot reload gives instant feedback. Manual path: 6 steps (plugin folder with `.claude-plugin/plugin.json`, `hooks/hooks.json`, a hooks `.mjs` file; draw with `ui.render` on `AbovePrompt`; keep data in `$.state` because hot reload resets module variables; `claude plugin validate` and `claude plugin test`; share via a `marketplace.json` on GitHub).
- Two advanced examples: "Blast Radius" (holds risky Bash commands such as `rm -rf`, shows what they would change, waits for confirmation) and "Replay Theater" (records edits in a turn, steps through them with a slash command).
- Install: `/plugin marketplace add your-org/my-mods`, `/plugin install token-weather@my-mods`, `/reload-plugins`. Warns mods run with Claude Code's privileges, so read before installing.
- Technical points: types auto-generated in `.claude-plugin/types/`; hot reload; `$.state.get/set`; UI redraws on state change; hooks get 10 seconds, waiting inside `$` calls does not count; validation via `claude plugin validate`.
- Says Claude Code's own features (AGENTS.md support, `/diff` pane) are built as open-source mods in `anthropics/claude-code`.

## 2. What mods can change

Per [MO] and [MR]: a mod can draw panes and a band above the prompt, restyle parts Claude Code draws (tool rows, spinner, the question dialog), hold/rewrite/answer tool calls and prompts, add slash commands and tools, call models, run timers, read/write files, start processes, make network requests. A mod is a plugin component alongside skills, agents, settings-style hooks and MCP servers ([P]). Compare table is in [MO] ("Compare mods, settings hooks, skills, and MCP servers").

Not changeable: a mod can restyle much of the UI "but not the permission prompt" ([MO]).

## 3. Claim check against first-party docs

Confirmed:

| Post claim | Confirmed by |
|---|---|
| A mod is a plugin whose JS/TS hooks run inside Claude Code | [MO] "A mod is a plugin that changes how Claude Code looks and behaves", [P] "A plugin that has one is called a mod" |
| `on('tool.call', { tool: 'Bash' }, async ($, e, next) => ...)` signature | [MR] "The hook function" section, [ME] |
| Observe / rewrite / answer | [MO] and [ME] use the same three words |
| Runs in terminal and desktop | [MO] "Where mods run" (also hooks run, but nothing draws, in the VS Code panel, `claude -p`, and cloud sessions) |
| Folder layout: `.claude-plugin/plugin.json`, `hooks/hooks.json`, a module file | [MR] "Files". Docs name the module `register.js` in examples, but any of `.js .mjs .cjs .ts ...` is allowed, so `.mjs` is fine |
| `ui.render` with component `AbovePrompt`, `$.ui.resolve(e)` returns `Box`/`Text` | [MR] "Render sites" and "Elements" |
| `$.state` get/set, state declared in `types/index.d.ts` | [MR] Files table and `$.state` row |
| `$.session.usage()` for context percent | [MR]: `usage()` returns `{ startedAt, context, rateLimits, cost }` and `context` has `tokens`, `window`, `percent` |
| `claude plugin validate` and `claude plugin test` | [MR] "Commands", [MC] |
| Types auto-generated in `.claude-plugin/types/` | [MC] "Get type definitions for your version" |
| Hot reload | [MC] (`--plugin-dir` reloads on save; each reload re-runs `register`, so module variables reset) |
| Install via `/plugin marketplace add`, `/plugin install name@market`, `/reload-plugins` | [MO] "Install or update a mod" (also `claude plugin install ...` in a shell); `/reload-plugins` is in [MR] Commands. The `marketplace add` form is standard plugin install flow ([P] links to it); the exact command was not shown on the pages fetched |
| Mods run with your privileges; install only from trusted sources | [MO] "Decide whether to trust a mod": not sandboxed, can read secrets and files, can approve tool calls |
| token-weather, blast-radius, replay-theater exist | [MO] "Try a sample mod" lists all three, in `anthropics/claude-code-playground` (not in the main repo) |
| `/diff` and AGENTS.md support are mods with public source | [MO] "Mods built into Claude Code" (`cc-plugin-diff`, `cc-plugin-agents-md`); [GH] `mods/` has `agents-md`, `diff`, `sec-default`, `telemetry`, `types` |
| Hook limit is 10 seconds | [MR] "Limits": 10 s per event (50 ms for `prompt.edit`) |

Flag: not confirmed, imprecise, or omitted by the post:

1. Time limit wording. [MR] says the 10 s excludes time inside `next` and inside any mods API call except `$.clock.sleep`. Time awaiting your own promises does count ([ME]). The post's "waiting in `$` calls doesn't count" is roughly right but loses the `next` and own-promise detail.
2. Version requirement not in the post. [MC] and [MO]: mods need Claude Code v2.1.287 or later.
3. "Auto-generated types" only applies to mods loaded from `--plugin-dir` or written by Claude in-session ([MC]); the post states it unconditionally.
4. Safety info the post omits: `--safe-mode`, `--bare` and `"disableAllHooks": true` turn mods off; org admins can restrict them ([MO]). A mod Claude writes in-session needs your approval and does not load in `claude -p`, `dontAsk` mode, untrusted workspaces ([MC]).
5. Sharing link `claude.ai/directory/manage`: not confirmed. The docs route submissions through "Anthropic's directory" via https://code.claude.com/docs/en/plugins/publish#submit-to-anthropics-directory ([MC]); that page and the claude.ai URL were not fetched.
6. token-weather details (the exact percent bands, icons, the roughly 80-line size, the 6-step walk-through) and the Blast Radius "hold pending confirmation" description were not checked line by line. The docs' description of blast-radius ("holds a risky shell command ... with buttons to proceed or cancel") agrees in spirit. The sample code lives at https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods and was not opened.
7. The post says mods are in "anthropics/claude-code" generally. The built-in mods are there, but the three tutorial mods are in the separate playground repo, which the docs say is shared "without support" ([MO]).

Nothing in the post contradicted the docs. No claim was found that the docs flatly deny.

## 4. Relevance to this project (FastAPI + vanilla JS SAT app)

The user's real question: can Claude customise itself here? Yes, and mods are the least relevant of the options.

- Mods change the Claude Code terminal/desktop UI and session behaviour. They do not touch or ship with the web app in `web/` or `server/`. Nothing in the SAT app needs one. A mod only fits if the user wants Claude Code itself to behave differently (a status band, a command guard).
- CLAUDE.md: already used (project `CLAUDE.md` with button and no-em-dash rules; global `~/.claude/CLAUDE.md`). [MEM]: CLAUDE.md is "context, not enforced configuration". Locations: `./CLAUDE.md` or `./.claude/CLAUDE.md` (project), `~/.claude/CLAUDE.md` (user), `./CLAUDE.local.md` (personal, gitignored), `@path` imports. `AGENTS.md` is read only when no CLAUDE.md exists in or above the working dir, so it is ignored here.
- Memory: already in use (`~/.claude/projects/.../memory/MEMORY.md`). [MEM] describes auto memory as notes Claude writes itself, loaded each session (first 200 lines or 25 KB).
- Hooks (settings hooks, no JS needed): the only mechanism the docs say actually enforces something. [MEM]: "To block an action regardless of what Claude decides, use a PreToolUse hook". [H]: configured in `~/.claude/settings.json`, `.claude/settings.json` (committable), `.claude/settings.local.json`, plugin `hooks/hooks.json`, or skill frontmatter; types are command, http, mcp_tool, prompt, agent. Concrete fit: the project rule "run `python3 tools/check-ui.py` before committing UI changes" is currently only a CLAUDE.md request, so Claude can skip it. A command hook on a post-edit or stop event could run it automatically. Not set up here; this is a suggestion only. The exact event to use was not verified beyond the event list in [H].
- Skills: [P] says a skill saved in `~/.claude/skills/` is available in every project, and that skills, subagents, hooks and MCP servers all work without a plugin. Good home for a repeatable procedure (for example "add a quiz topic") rather than bloating CLAUDE.md ([MEM] recommends moving multi-step procedures to skills). The project-level skills folder path was not on the pages fetched, so confirm at https://code.claude.com/docs/en/skills before relying on it.
- Plugins: only worthwhile if the same setup is wanted in many repos or for teammates ([P] "Decide whether you need a plugin"). Not needed for a solo project.
- Safety if a mod is ever installed: it runs unsandboxed with the user's permissions ([MO]). Use `claude plugin validate <dir>` first to list its hooks and calls.

Bottom line: keep using CLAUDE.md and memory for guidance; use a settings hook for anything that must always happen (the check-ui script); skip mods unless the user wants to change how Claude Code itself looks or guards commands.
