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
- `references/games/`: machine-readable game packs and `index.json`.
- `references/game-onboarding.md`: source discovery, A/B/C/D/E grading, and the onboarding gate for arbitrary games.
- `scripts/`: game-profile loader, validator, drafting helpers, probe harness, output guard.
- `tests/`: negative fixtures and fixture generator.

## Rules for changes

1. Do not remove or weaken hard gates without a review record.
2. Keep `README.md` Chinese-first; keep `README.en.md` in sync.
3. New game support goes through `references/game-onboarding.md`: scaffold with `scripts/game_profile.py init`, complete `references/sources/<id>.md`, pass `game-check`, then update the human-readable registry and docs. Do not reintroduce hardcoded game/title constants in the validator.
4. Non-Chinese official text: keep the original quote and the Chinese translation in separate columns (`sources.md` §4, `style.md` §3/appendix), fill `source_languages` / `translation_policy` / `translation_source` in all three frontmatter files, and never present a community translation as official Chinese.
5. New rules need a negative fixture or regression check.
6. Never commit generated persona directories, credentials, tokens, or local absolute paths.
7. Run `python scripts/selftest.py` before committing.

## Common commands

```bash
python scripts/selftest.py
python scripts/game_profile.py check
python scripts/game_profile.py game-check <id>
python scripts/validate_persona.py assets/examples/standard/qingxiao --strict --explain
python scripts/persona_tools.py check assets/examples/standard/qingxiao
```
