# Character Persona Forge

**English** | [简体中文](README.md)

[![Version](https://img.shields.io/badge/version-1.5.1-blue.svg)](#)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![selftest](https://img.shields.io/badge/selftest-23%2F23-brightgreen.svg)](#validation)

> Compile a game character into **auditable, injectable, testable** persona documents.

`character-persona-forge` is an Agent Skill for producing portable persona files for characters from Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, and Wuthering Waves. Instead of “write a character card from memory”, it connects official sources, evidence grading, persona boundaries, runtime injection, and reproducible self-checks into one auditable pipeline.

---

## Why Not Just a Character Card?

| Ordinary character card | Character Persona Forge |
|---|---|
| Facts and quotes often lack provenance | Every core fact and quote carries `[S##]` / `[E##]` IDs |
| The persona collapses back into an assistant after a few turns | CORE injection, identity anchors, post-history instructions, and an OOC state machine |
| “Does it feel in character?” is the only test | 12 OOC probes + 10 adversarial probes + cold-start test |
| No clear delivery gate | Budget, matrix, evidence landing, quote quotas, and identity safety are hard gates |
| Tied to one host | The same files work in Claude Code, Codex, Trae, Qoder, WorkBuddy, DSH, and more |

---

## Output

```text
personas/<game>/<character>/
├── soul.md      # Who I am: identity, history, motives, relationships, knowledge limits, OOC rules
├── style.md     # How I speak: register, sentence rhythm, verbal tics, examples, style red lines
└── sources.md   # Evidence archive: sources, quotes, inferences, conflicts, coverage matrix, self-check
```

`soul.md` and `style.md` are split into **CORE** and **APPENDIX**. CORE can be injected alone; APPENDIX holds stage details, extended corpus, and evidence indexes. `sources.md` is never injected; it is for audit and future updates.

---

## Highlights

- **Official sources first**: S1 official first-party > S2 official platform > S3 community wiki > S4 analysis/fanwork. Gaps must be labeled as community transcripts.
- **Two-phase writing**: freeze source/evidence IDs before writing the body, avoiding “write first, find sources later” rework.
- **Portable CORE**: core sections are self-contained; appendices load only when needed.
- **Runtime integration**: three-layer injection model, OOC state machine, 51 host mappings, output guard.
- **Tooling**: per-section budget report, evidence-landing map, §7 matrix stub, probe harness, structure validator.
- **Bilingual triggers**: Chinese and English game/character names are supported.

---

## Install

Copy the whole `character-persona-forge/` folder into your host's skills directory.

| Host | Common global path | Project-level path |
|---|---|---|
| Claude Code | `~/.claude/skills/character-persona-forge/` | `.claude/skills/character-persona-forge/` |
| Codex / shared Agent Skills | `~/.agents/skills/character-persona-forge/` | `.agents/skills/character-persona-forge/` |
| DeepSeek Harness (DSH) | `~/.dsh/skills/character-persona-forge/` | `.dsh/skills/character-persona-forge/` |
| Trae CN | `~/.trae-cn/skills/character-persona-forge/` | `.trae/skills/character-persona-forge/` |
| Trae International | `~/.trae/skills/character-persona-forge/` | `.trae/skills/character-persona-forge/` |
| Qoder | `~/.qoder/skills/character-persona-forge/` | `.qoder/skills/character-persona-forge/` |
| WorkBuddy | `~/.workbuddy/skills/character-persona-forge/` | Follow host conventions |

Restart or reload the host, then ask:

```text
Use Skill: character-persona-forge
Create a persona document for Nahida from Genshin Impact
```

---

## Workflow

1. **Plan gate**: the first reply contains only a four-row plan + cost/time warning + confirmation question. No web access or file writes before approval.
2. **Research**: official sources first, community sources only for gaps; write `sources.md` as you go.
3. **Freeze IDs**: finalize the source and evidence tables before writing the body.
4. **Write body**: write CORE of `soul.md` / `style.md`, then appendices.
5. **Self-check**: budget, evidence landing, matrix, structural validation, 12 + 10 probes.
6. **Deliver**: report paths, source counts, gaps, probe scores, and usage instructions.

---

## Validation

Python 3.9+ is required; all scripts use the standard library only.

```bash
# 1. Validator regression
python scripts/selftest.py

# 2. Drafting helpers: budget / evidence landing / matrix stub
python scripts/persona_tools.py check personas/<game>/<character>

# 3. Structural validation
python scripts/validate_persona.py personas/<game>/<character> --strict --explain
```

Common subcommands:

```bash
python scripts/persona_tools.py budget personas/<game>/<character>
python scripts/persona_tools.py evidence-map personas/<game>/<character>
python scripts/persona_tools.py matrix-stub personas/<game>/<character>
python scripts/probe_harness.py gen-prompts personas/<game>/<character> --out-dir research/probe
python scripts/check_output.py reply.md
```

---

## Quality Gates

- CORE budget: quick ≤4,000; standard ≤8,000; deep ≤12,000 CJK.
- Sources/evidence: quick ≤10 / 8–15; standard ≤25 / 20–40; deep ≤50 / 40–80.
- Coverage matrix: soul 1–8 + style 1–6 (14 rows); official/community counts must match actual citations.
- 12 OOC probes: average ≥4.0, no score ≤2.
- 10 adversarial probes: average ≥4.0, no score ≤2; items 1/4/5/6 must not be 1.
- When seriously asked whether it is an AI, it must answer truthfully and must not claim to be a real human.
- Explicit sexual content, sexualization of minors, leaked/unreleased content, impersonation, and fraud are prohibition-level and are never unlocked by confirmation.

---

## Repository Layout

```text
.
├── SKILL.md                  # Skill entrypoint
├── README.md                 # Chinese README (default)
├── README.en.md              # English README
├── CHANGELOG.md
├── LICENSE                   # CC BY-NC-SA 4.0
├── references/               # Workflow, confirmation, source policy, rubric, runtime integration
├── assets/
│   ├── templates/            # soul/style/sources templates (standard + quick)
│   └── examples/             # Standard/quick reference examples
├── scripts/                  # Validator, drafting helpers, probe harness
└── tests/                    # Negative regression fixtures
```

---

## Good Fit / Not a Good Fit

**Good fit:**

- You want a long-lived persona document for a game character.
- You need clear separation between official canon, community transcripts, and inference.
- You want the same persona to work across multiple agent hosts.
- You need reproducible OOC and boundary tests.

**Not a good fit:**

- Pure card art, avatar generation, or stat guides.
- “Write from memory” when no sources exist and the user refuses to provide material.
- Bypassing platform safety policies, impersonating real people, or using leaked content.

---

## License and Notices

Original documentation, templates, scripts, and examples in this repository are released under **[CC BY-NC-SA 4.0](LICENSE)**. You may share and adapt them with attribution, for non-commercial purposes only, and derivative works must use the same license.

> Note: Creative Commons does not recommend using CC licenses for software itself. This project uses the license uniformly as requested; if you need to use the scripts for commercial or software-distribution purposes, contact the maintainer to discuss separate licensing.

- **Commercial use is not permitted**; contact the maintainer for separate commercial licensing.
- Game characters, names, official dialogue, and lore remain the property of their respective rights holders.
- This is a fan-made workflow tool, not affiliated with or endorsed by HoYoverse, miHoYo, or Kuro Games.
- Official material is quoted only for commentary, research, and style calibration. Respect source-site terms and avoid bulk scraping.
- Generated documents are intended for personal, non-commercial roleplay. Check local law and platform rules before publishing them.

---

## Contributing

Issues and PRs are welcome. Before submitting, run:

```bash
python scripts/selftest.py
```

When adding a rule, add a negative fixture or regression check as well; “documented but unenforced” is treated as a bug.
