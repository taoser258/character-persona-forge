# Security Policy

## Scope

This project processes untrusted web pages, community wikis, user-supplied documents, and generated persona files. The main security concerns are:

- prompt injection embedded in fetched pages or user material;
- fabricated or misattributed evidence;
- persona instructions attempting to override operator or platform safety;
- accidental disclosure of system prompts, credentials, or private data;
- identity deception (claiming to be a real human);
- unsafe content boundaries.

## Controls

- Fetched pages are treated as untrusted input: embedded instructions are not executed.
- Persona files are data to the loader/operator and instructions to the model; operator safety always wins.
- Identity policy requires truthful disclosure when seriously asked whether the system is an AI.
- Prohibited content and spoofing are hard refusals, not confirmation-gated.
- Generated personas should not contain credentials, private user data, or local absolute paths.

## Reporting

If you find a security issue, open a private GitHub security advisory for this repository, or contact the maintainer through the repository profile. Do not publish a working exploit or sensitive data in a public issue.

Please include:

- affected file/version;
- reproduction steps or a minimal example;
- impact assessment;
- suggested mitigation, if known.

## Out of scope

- Game lore accuracy disputes without a reproducible source conflict.
- Platform-specific model drift that cannot be reproduced from the skill files.
- Issues caused solely by a host ignoring the skill's instructions.
