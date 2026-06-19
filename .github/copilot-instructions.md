# Copilot Instructions for Otimous (Discord bot)

## Quick run / build / test / lint

- Run the bot locally: set DISCORD_TOKEN in .env then:
  - python main.py
- Procfile (Heroku): `worker: python main.py`
- Dependencies: `pip install -r requirements.txt`
- Tests: None present in the repository. No test runner configured.
- Lint/format: No linter/formatter config detected. Add one (flake8/ruff/black) if desired.

## High-level architecture

- Entry: main.py defines Otimous(commands.Bot)
  - setup_hook loads cogs (cogs.avatar, cogs.scheduler, cogs.hiddenavatar) and syncs app commands.
  - Bot runs with token from environment and logs to `discord.log`.

- Cogs/Commands (cogs/)
  - avatar.py: slash commands to show avatars (visible & hidden variants).
  - hiddenavatar.py: variant that sends avatar to channel and replies ephemerally.
  - scheduler.py: admin-only slash commands to schedule periodic avatar posts and a background tasks.loop that checks/sends them.

- Persistence
  - data/avatar_config.json: primary JSON store for scheduled avatar config (used by utils/config_manager.py).
  - utils/config_manager.py: read/write helpers for data/avatar_config.json.
  - utils/database.py: contains an SQLite schema and helper functions (avatar.db). Currently present but not referenced by cogs — treat as an optional/alternate persistence layer.

- Background work
  - AvatarScheduler starts a tasks.loop to check schedules every 30s and updates last_sent timestamps in the JSON config.

## Key repository conventions and patterns

- Cogs use the async setup pattern: `async def setup(bot): await bot.add_cog(...)` — Copilot should follow this when adding new cogs.
- Slash commands use discord.app_commands and return ephemeral responses for confirmations where appropriate.
- Scheduling is stored per-guild under data/avatar_config.json keyed by guild id (string). Fields: member_id, channel_id, interval_minutes, last_sent.
- Permissions: admin-only commands use `@app_commands.default_permissions(administrator=True)`.
- Time values are stored as UNIX timestamps (seconds) and intervals are stored in minutes.
- Code and messages are Portuguese; new command names and descriptions should follow the existing language.
- Environment: token loaded via python-dotenv (.env) and main reads DISCORD_TOKEN.
- Logging: a FileHandler writes to `discord.log` (main.py). Keep log I/O in mind for CI or containerized runs.

## Existing docs and AI configs incorporated

- No README.md or CONTRIBUTING.md present to extract; requirements.txt and Procfile were used to infer run commands.
- No AI assistant config files (CLAUDE.md, .cursorrules, AGENTS.md, .windsurfrules, etc.) detected.

---

If edits are made that add tests, linters, or CI workflow files, update this file to include the exact commands and examples (how to run a single test, how to run a single linter pass, etc.).
