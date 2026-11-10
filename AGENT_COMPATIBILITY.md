# Shared knowledge entry points across coding agents

Research checked: 2026-11-02. This records documented file-loading behavior, not runtime tests of every client.

| Tool / layer | Project entry file | How the shared context is connected | Practical limit |
|---|---|---|---|
| Codex | `AGENTS.md` | Auto-discovers instructions in the project path. This library's `AGENTS.md` directs genome tasks to `AI_CONTEXT.md`. | It does not discover a knowledge library outside the active project root. Keep the instruction short; default project instruction limit is 32 KiB. |
| Claude Code | `CLAUDE.md` | This library's `CLAUDE.md` imports `AGENTS.md` and `AI_CONTEXT.md` with `@...`. Current Claude Code can also read `AGENTS.md`, but a `CLAUDE.md` in the path takes precedence by default, so the explicit import avoids losing shared rules. | Direct AGENTS support is documented for Claude Code v2.1.277+; the CLAUDE.md bridge also makes the shared source explicit. |
| Gemini CLI | `GEMINI.md` | This library's `GEMINI.md` imports the same two files using `@./...`. Gemini supports hierarchical context and imports. | Loads project context only when Gemini CLI is run in the library/project path or otherwise given the files. |
| DeepSeek model/API | No universal repository filename established in the official API docs checked | Use a local coding harness/IDE to read `AGENTS.md` or `OTHER_AI_PROMPT.md`, then pass relevant notes to the model. The API supports a system instruction, so a harness can supply the shared prompt. | DeepSeek chat API is stateless; caller must include conversation context. The model cannot read local files unless the harness/tool exposes them. |
| Other coding agents | Varies by agent/harness | Configure the harness to load `AGENTS.md`, or use `OTHER_AI_PROMPT.md` and point it to `AI_CONTEXT.md`. | Plain Markdown is portable, but auto-loading is a feature of each host tool, not of the model itself. |

## Verification commands documented by vendors

- Codex: ask it to list active instruction sources or summarize its instructions from the library root.
- Claude Code: run `/memory` or `/context` to inspect loaded project memory.
- Gemini CLI: run `/memory show` to inspect concatenated context.
- DeepSeek/API harness: inspect the system prompt and files passed to the model; the API itself does not retain prior request context.

## Official documentation

- Codex `AGENTS.md`: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- Claude Code memory and AGENTS support: https://code.claude.com/docs/en/memory
- Gemini CLI context files: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
- DeepSeek multi-round chat state: https://api-docs.deepseek.com/guides/multi_round_chat/
- DeepSeek chat API roles/content: https://api-docs.deepseek.com/api/create-chat-completion/

## Scope

The adapters and mappings here were written, but this machine session did not launch Codex CLI, Claude Code, Gemini CLI, or a DeepSeek-backed coding harness to test their runtime file discovery. The knowledge files themselves are plain Markdown. Verify each host's loaded-context view after configuring it.
