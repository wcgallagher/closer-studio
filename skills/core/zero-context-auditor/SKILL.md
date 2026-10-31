---
name: zero-context-auditor
description: Mandatory gate before creating or editing any skill file (SKILL.md), CLAUDE.md, script, or factual deliverable (VSL script, ad copy, report). Extracts every claim, number, name, file path, command and tool the draft relies on, proves each one against a real source (repo file, tool output, transcript, the user's own words), and blocks anything unsourced. Run it whenever you are about to write or change a skill, when a draft states facts about the business, or when the user says "audit", "verify", "zero context", "don't hallucinate" or "are you sure".
---

# Zero-Context Auditor

Axiom: if it is not in a file, a tool result, a transcript, or the user's own words in this session, it does not
exist. Confident guesses are the most expensive failure: a wrong skill file repeats its error in every future
session that loads it.

## When it runs

- Before writing or editing any `SKILL.md`, `CLAUDE.md` or agent instruction file. No exceptions.
- Before shipping copy, scripts or reports that state facts about the business, a client or the market.
- When asked whether something is true.

## Step 1. Extract every claim

Read the draft line by line and list each:

| Type | Examples |
|---|---|
| Fact | "$3.8M placed in 2025", "average deal $120K", "50/50 split" |
| Name | people, companies, products, domains, handles |
| Path | a file of the Set More Annuities repo, the VSL render script of that repo |
| Command / tool | `python x.py --flag`, `mcp__server__tool`, an ffmpeg filter |
| Behaviour claim | "this script trims silences", "the API returns X" |
| Rule | "never say annuity in client copy" |

## Step 2. Prove each one

For every claim, find the source and record it. Accepted sources, strongest first:

1. **FILE**: path and line, with the quoted text (`grep -n` it, don't remember it).
2. **TOOL**: the tool call that returned it in this session, with the returned value.
3. **TRANSCRIPT**: the take and timestamp where it was said.
4. **USER**: the user's own message in this session, quoted.
5. **RUN**: for commands and paths, you executed it (or `ls`, `--help`, a dry run) and it worked.

Not accepted: memory, "common knowledge" about this business, a previous session you can't see, another
model's summary you did not check, a filename that merely sounds right.

## Step 3. Classify and act

| Status | Meaning | Action |
|---|---|---|
| VERIFIED | Source found and quoted | Keep |
| USER-STATED | Only the user said it | Keep, marked as the user's claim if it is a number or result |
| INFERRED | Follows from verified facts | Keep only if the reasoning is one step; say it is inferred |
| UNSOURCED | No source | Delete, or replace with `[DATA GAP: what is missing]` |
| CONTRADICTED | Sources disagree | Stop and show both sources to the user |

## Step 4. Run the checker

```bash
python3 <this skill>/scripts/audit_skill.py <path/to/SKILL.md>
```

It fails when: frontmatter is missing `name` or `description`, a relative path or script the skill references does
not exist, or a number, dollar figure or percentage in the skill has no row in the skill's `AUDIT.md`.

## Step 5. Write AUDIT.md next to the skill

```markdown
| Claim | Status | Source |
|---|---|---|
| $3.8M placed in 2025 | VERIFIED | CLAUDE.md:9 "Chase Gallagher proved manually: $3.8M in annuity premium placed in 2025" |
| sellmoreannuities.com | VERIFIED | CLAUDE.md:9 "SellMoreAnnuities.com (SMA) is an AI agent platform" |
| the VSL build script of the Set More Annuities repo | RUN | `python3 vsl/pipeline/v3_build.py ... --preview` exit 0 |
```

Commit AUDIT.md with the skill. A skill without one is a draft, not a skill.

## Step 6. Report

End with one line: `AUDIT: <n> claims, <v> verified, <u> user-stated, <g> gaps, <c> contradictions.` List every gap
and contradiction by name. Never report a pass you did not run.
