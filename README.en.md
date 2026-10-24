# Character Persona Forge

**English** | [简体中文](README.md)

[![Version](https://img.shields.io/badge/version-1.7.0-blue.svg)](#)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![selftest](https://img.shields.io/badge/selftest-29%2F29-brightgreen.svg)](#validation)

> Compile a game character into **auditable, injectable, testable** persona documents.

`character-persona-forge` is an Agent Skill that connects official sources, evidence grading, persona boundaries, runtime injection, and reproducible self-checks into one auditable pipeline. It produces `soul.md`, `style.md`, and `sources.md`, plus an optional `injection.md` copy-ready pack.

It is not a "let the model improvise a roleplay prompt" generator. It is a source → evidence → persona contract → self-check workflow. Nine **optimized and tested Game Packs** are built in: six curated games plus provisional Black Myth: Wukong, Hades, and Night in the Woods. **Support is not limited to them**: any game with retrievable sources can be onboarded through `references/game-onboarding.md`.

---

## Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [Output](#output)
- [Optimized and Tested Games](#optimized-and-tested-games)
- [How a Persona Document Is Made](#how-a-persona-document-is-made)
- [Keeping the Persona Alive](#keeping-the-persona-alive)
- [Validation](#validation)
- [Quality Gates](#quality-gates)
- [Repository Architecture](#repository-architecture)
- [Adding a Game](#adding-a-game)
- [Good Fit / Not a Good Fit](#good-fit--not-a-good-fit)
- [License and Notices](#license-and-notices)

---

## Install

### Option A: Ask an Agent to Install It (Recommended)

Send this to a host that supports Agent Skills (Claude Code, Codex, Cursor, ZCode, WorkBuddy, etc.):

> Install this skill for me: https://github.com/taoser258/character-persona-forge

The agent will place the repository in the host's skills directory and check that `SKILL.md` is readable. If the host does not support automatic installation, use Option B.

### Option B: Manual Install

```bash
git clone https://github.com/taoser258/character-persona-forge.git
# Replace $SKILLS_DIR with the host's skills directory
cp -r character-persona-forge "$SKILLS_DIR/character-persona-forge"
```

Common locations differ by host (e.g. `~/.claude/skills/`, `.agents/skills/`, `~/.zcode/skills/`). See `references/runtime-integration.md` §6 for the full 51-host mapping.

### Verify the Install

```bash
cd "$SKILLS_DIR/character-persona-forge"
python scripts/selftest.py
# Expected: 29/29 checks passed
```

---

## Quick Start

Tell the agent:

> Use character-persona-forge to create a quick persona document for Erlang Shen from Black Myth: Wukong.

The first reply will contain:

1. Official sources to check
2. Character-level S1 probe
3. Main gaps
4. Output directory plan
5. Questions to confirm
6. Cost/time estimate

It will not browse or write files until you confirm. When the documents are ready, open `injection.md`, copy everything, and paste it into the AI's custom instructions / character settings / system prompt. If there is no such field, send it as the first message. Say "break character / OOC / exit role" to pause.

For the full beginner guide, see `references/usage-guide.md`; for advanced runtime setup, see `references/runtime-integration.md`.

---

## Output

| File | Purpose | Injected? |
|---|---|---|
| `soul.md` | Identity, persona tensions, motives, relationships, knowledge/memory boundaries, OOC red lines | Yes (CORE) |
| `style.md` | Language fingerprint, scene registers, official dialogue, examples, style red lines | Yes (CORE) |
| `sources.md` | Sources, evidence, inferences, conflicts, coverage matrix, self-check and probes | No, for audit |
| `injection.md` | Identity directive + soul/style CORE, copy-ready | Yes |

Default directory: `personas/<game-directory>/<character>/`. The three audit documents are the source of truth; `injection.md` is a derived convenience file.

---

## Optimized and Tested Games

These games have dedicated source work, prompt calibration, and real test runs, so persona generation is more stable. **This is not the full support scope.** Any other game can be onboarded through `references/game-onboarding.md`.

| Game | Status | Fixed protagonist title | Source profile |
|---|---|---|---|
| Genshin Impact | curated | Traveler | `genshin.md` |
| Honkai: Star Rail | curated | Trailblazer | `hsr.md` |
| Zenless Zone Zero | curated | Proxy | `zzz.md` |
| Wuthering Waves | curated | Rover | `wuwa.md` |
| Arknights | curated | Doctor | `arknights.md` |
| Arknights: Endfield | curated | Administrator | `arknights-endfield.md` |
| Black Myth: Wukong | provisional | Destined One (天命人) | `black-myth-wukong.md` |
| Hades | provisional | Zagreus | `hades.md` |
| Night in the Woods | provisional | Mae | `night-in-the-woods.md` |

All source profiles live in `references/sources/`.

Notes:

- **provisional** means the pack metadata has not been confirmed by the user. It does not block generation, but the plan must say so.
- A game-level A landscape does not guarantee character-level S1. Black Myth is an A-grade game, but Erlang Shen has no official character page; 12/14 chapters were labeled `community-only` / `derived`.
- Arbitrary-game onboarding, A/B/C/D/E grading, and depth caps are documented in `references/game-onboarding.md`.

---

## How a Persona Document Is Made

| Stage | Output | Gate |
|---|---|---|
| 1. Plan | Four-line plan + cost/time + confirmation | No browsing or writing before approval |
| 2. Source discovery | Source profile + A/B/C/D/E grade | Stop if no sources |
| 3. Evidence | `sources.md` source and evidence tables | S1–S4 grading; community transcripts labeled |
| 4. Freeze IDs | `[S##]` / `[E##]` / `[I##]` / `[C##]` | Evidence before prose |
| 5. Extraction | Identity, persona, motives, relationships, boundaries, emotions, language | Observable behavior, not labels |
| 6. Writing | `soul.md` / `style.md` CORE + APPENDIX | CORE independently injectable |
| 7. Validation | Validator + selftest | Structure, budgets, matrix, translation gates |
| 8. Acceptance | 12 OOC + 10 adversarial probes, `injection.md` | No delivery on FAIL |

Source tiers: S1 official first-party, S2 official platform/licensed, S3 community wiki/transcript, S4 analysis/fan work. Prefer S1; use S3 only for gaps and label it.

For detailed workflow, failure modes, and compression order, see `references/workflow.md`; for scoring and critical failures, see `references/quality-rubric.md`.

---

## Keeping the Persona Alive

Pasting the documents into a system prompt is not enough. Use three layers:

1. **System layer**: identity directive + soul/style CORE in the system prompt or persistent instructions.
2. **Anchor layer**: every 10–20 turns or after tool calls, inject a 5–10 line identity anchor.
3. **Post-history layer**: where supported, append a retention instruction at the end of the conversation.

The documents also include identity anchors, an OOC state machine, knowledge/memory boundaries, output guards, and spoiler gates. Full setup and the 51-host mapping are in `references/runtime-integration.md`.

---

## Validation

Python 3.9+ is required; all scripts use the standard library only.

```bash
# 0. New-game onboarding (optional)
python scripts/game_profile.py init --id <id> --display-name "<name>" --title "<protagonist title>" --landscape <A/B/C/D/E>
python scripts/game_profile.py game-check <id>

# 1. Game packs and regression
python scripts/game_profile.py check
python scripts/selftest.py

# 2. Drafting helpers
python scripts/persona_tools.py check personas/<game>/<character>

# 3. Structural validation
python scripts/validate_persona.py personas/<game>/<character> --strict --explain
```

`scripts/selftest.py` covers 2 positive examples + 5 negative fixtures + Game Pack / `game-init` / non-Chinese translation / non-Chinese quote quota / research-depth consistency regressions. It currently passes **29/29**.

Common subcommands:

```bash
python scripts/persona_tools.py budget personas/<game>/<character>
python scripts/persona_tools.py matrix-preview personas/<game>/<character>
python scripts/persona_tools.py pack personas/<game>/<character>
python scripts/probe_harness.py gen-prompts personas/<game>/<character> --out-dir research/probe
```

---

## Quality Gates

- CORE budgets: quick ≤4,000; standard ≤8,000; deep ≤12,000 CJK.
- Sources/evidence: quick ≤10 / 8–15; standard ≤25 / 20–40; deep ≤50 / 40–80.
- Coverage matrix: soul 1–8 + style 1–6 (14 rows); official/community counts must match actual citations.
- 12 OOC probes: average ≥4.0, no score ≤2; 10 adversarial probes: average ≥4.0, no score ≤2.
- When sincerely asked whether it is an AI, the persona must answer honestly and never claim to be a real human.
- Explicit sexual content, sexualized minors, leaked/unreleased content, impersonation, and fraud are prohibited.

---

## Repository Architecture

```text
character-persona-forge/
├── SKILL.md                 # Skill entry and hard gates
├── README.md / README.en.md # Chinese-first bilingual docs
├── AGENTS.md                # Repository rules
├── THIRD_PARTY_NOTICES.md   # Third-party sources and licensing
├── assets/
│   ├── templates/           # soul/style/sources/game-profile templates
│   └── examples/            # standard/quick examples
├── references/
│   ├── game-onboarding.md   # Arbitrary-game onboarding
│   ├── games/               # Game Pack JSON + schema
│   ├── sources/             # Per-game source profiles
│   ├── workflow.md          # End-to-end workflow
│   ├── quality-rubric.md    # Scoring and probes
│   └── runtime-integration.md
├── scripts/
│   ├── game_profile.py      # Pack validation / init / game-check
│   ├── validate_persona.py  # Structure, budgets, matrix, translation
│   ├── persona_tools.py     # Budgets, matrices, injection pack
│   ├── probe_harness.py     # Probe packages and reports
│   ├── check_output.py      # Reply output guard
│   └── selftest.py          # 29 regression checks
└── tests/                   # Negative fixtures and generator
```

---

## Adding a Game

1. Run source discovery and A/B/C/D/E grading via `references/game-onboarding.md`.
2. Use `game-init` to create the provisional pack, source skeleton, and index entry.
3. Complete `references/sources/<id>.md` and clear every TODO.
4. Run `game-check` until `READY`; after user confirmation, change `status` to `curated`.
5. Update `references/source-registry.md`, both READMEs, then run `check` and `selftest.py`.

v1.7 supports fixed protagonists with live-service or complete linear canon only. Selectable/custom/ensemble protagonists and branching/remake/EA/sandbox canon are reserved. D-grade sources are quick-only and require explicit CONDITIONAL acceptance; E-grade sources are refused.

---

## Good Fit / Not a Good Fit

**Good fit:**

- Long-lived, auditable persona documents for game characters;
- Stable character voice across multi-turn conversations;
- Auditing an existing persona for sources, OOC, and boundaries.

**Not a good fit:**

- Original characters, stat/team guides, or live game boosting;
- A character name with no retrievable sources and no material from the user;
- A one-off character card or a short prompt.

---

## License and Notices

Original documentation, templates, scripts, and examples are released under **[CC BY-NC-SA 4.0](LICENSE)**. You may share and adapt them with attribution, for non-commercial purposes only, and derivative works must use the same license.

- **Commercial use is not permitted**; contact the maintainer for separate commercial licensing.
- Game characters, names, official dialogue, and lore remain the property of their respective rights holders.
- This is a fan-made workflow tool, not affiliated with or endorsed by HoYoverse, miHoYo, Kuro Games, Hypergryph, Supergiant Games, Infinite Fall, or Finji.
- Third-party community transcription sources and their status are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); the repository does not bundle scripts, subtitles, or voice files.
- Official material is quoted only for commentary, research, and style calibration. Respect source-site terms.

---

## Contributing

Issues and PRs are welcome. Before submitting, run:

```bash
python scripts/selftest.py
python scripts/persona_tools.py check assets/examples/standard/qingxiao
python scripts/validate_persona.py assets/examples/standard/qingxiao --strict --explain
```

New rules must include a negative fixture or regression check. See `CONTRIBUTING.md`.
