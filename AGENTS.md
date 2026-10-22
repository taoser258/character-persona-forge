# AGENTS.md

This repository is a single-skill Agent Skills project. The repository root is the skill folder.

## Read first

- `SKILL.md`: workflow, hard gates, output contract.
- `references/confirmation.md`: A/B/C confirmation policy.
- `references/quality-rubric.md`: scoring and critical failures.
- `references/source-policy.md`: source tiers, evidence rules, quote quotas.

## Repository map

- `assets/templates/`: soul/style/sources templates.
- `assets/examples/`: standard/quick reference examples.
- `references/sources/`: per-game source profiles.
- `scripts/`: validator, drafting helpers, probe harness, output guard.
- `tests/`: negative fixtures and fixture generator.

## Rules for changes

1. Do not remove or weaken hard gates without a review record.
2. Keep `README.md` Chinese-first; keep `README.en.md` in sync.
3. New game support goes in `references/sources/<game>.md`, plus the registry index, `SKILL.md` input table, and validator game/title constants.
4. New rules need a negative fixture or regression check.
5. Never commit generated persona directories, credentials, tokens, or local absolute paths.
6. Run `python scripts/selftest.py` before committing.

## Common commands

```bash
python scripts/selftest.py
python scripts/validate_persona.py assets/examples/standard/qingxiao --strict --explain
python scripts/persona_tools.py check assets/examples/standard/qingxiao
```
