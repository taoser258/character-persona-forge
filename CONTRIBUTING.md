# Contributing

Thanks for improving Character Persona Forge. This repository is a single-skill Agent Skills project; the root is the skill folder.

## What to contribute

- **New game source profiles**: add an official-source registry and retrieval notes for another game.
- **Evidence/validator improvements**: better checks, fixtures, or clearer errors.
- **Templates/examples**: stronger personas, better calibration, bilingual docs.
- **Runtime integration**: host mappings, identity anchors, output guards.
- **Bug reports**: broken links, false positives/negatives, unclear workflow.

## Before submitting

```bash
python scripts/selftest.py
python scripts/persona_tools.py check assets/examples/standard/qingxiao
python scripts/validate_persona.py assets/examples/standard/qingxiao --strict --explain
```

- Keep `README.md` (Chinese) and `README.en.md` in sync.
- Add a negative fixture or regression check when adding a rule.
- Do not commit `__pycache__`, tokens, credentials, generated personas, or local absolute paths.
- Keep evidence quotes short; do not copy full quests, lyrics, or paid text.

## Adding a new game

1. Follow `references/game-onboarding.md`: discover sources, assign A/B/C/D/E, and confirm the depth with the user.
2. Scaffold with `python scripts/game_profile.py init ...`; it creates the pack, source skeleton, and index entry.
3. Complete `references/sources/<id>.md` and clear every `TODO`.
4. Run `python scripts/game_profile.py game-check <id>` until it returns `READY`; after user confirmation, change `status` to `curated`.
5. Update the human-readable index in `references/source-registry.md` and the README game table.
6. Run `python scripts/game_profile.py check` and `python scripts/selftest.py`.

v1.7 supports fixed protagonists and live-service/complete linear canon only. Do not add custom-protagonist or branching packs yet; those modes are reserved for a later schema/validator release. D-grade sources are quick-only and require explicit CONDITIONAL acceptance; E-grade sources are refused.

For non-Chinese official text, keep the original quote and a Chinese translation in separate columns, fill `source_languages` / `translation_policy` / `translation_source` in all three persona frontmatter files, and label the translation. Never present a community translation as official Chinese. See `references/games/schema.md` §6 and `references/source-policy.md` §3.0.

## License

By contributing, you agree that your contribution is licensed under the repository's **CC BY-NC-SA 4.0** terms. See `LICENSE`.

Game names, characters, and official text remain the property of their rights holders. Do not contribute leaked or unreleased material.
