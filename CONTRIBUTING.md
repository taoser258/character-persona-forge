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

1. Add `references/sources/<game>.md` with official entries, gaps, search patterns, and community fallbacks.
2. Add it to `references/source-registry.md`.
3. Update the game table in `SKILL.md`.
4. Update `ALLOWED_GAMES`, `EXPECTED_USER`, and the fixed protagonist title in `scripts/validate_persona.py`.
5. Update README "Supported games" and host notes.
6. Add a small fixture or example if the new game has different terminology.
7. Run `python scripts/selftest.py`.

## License

By contributing, you agree that your contribution is licensed under the repository's **CC BY-NC-SA 4.0** terms. See `LICENSE`.

Game names, characters, and official text remain the property of their rights holders. Do not contribute leaked or unreleased material.
