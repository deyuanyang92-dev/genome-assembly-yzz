# Reusable prompt for coding agents without automatic project-file discovery

Use this as the initial project instruction in an IDE, agent harness, or chat tool that does not automatically load repository context files:

> Before changing code related to genome assembly or polychaete genomics, read the shared AI context at `/mnt/p/yzz-全基因组工作流程/genome-assembly-yzz/AI_CONTEXT.md`, then read the relevant linked notes and version ledger. Reuse completed work when its exact software version, data and scope match. Verify any changed version or production-scale assumption. Distinguish published/documented behavior, source inspection and executed evidence. Preserve provenance, versions, timestamps and limitations in new work. Do not claim access to local files unless the connected agent environment has actually mounted them; if not, ask me to attach the specific files named by AI_CONTEXT.md.

## DeepSeek and other model backends

The model is not the filesystem reader. A coding harness or IDE must expose the local repository and load its project instruction file. When DeepSeek is used through a harness that reads `AGENTS.md`, `CLAUDE.md` or `GEMINI.md`, use the matching adapter there. When using a chat/API without local workspace access, provide this prompt and attach `AI_CONTEXT.md` plus the exact referenced note/ledger. Do not upload the full genome data bundle unless a task needs it.
