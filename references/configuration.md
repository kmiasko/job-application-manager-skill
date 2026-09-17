# Configuration

Resolve the data store before reading project settings or dispatching agents.

## Per-user settings

Use the first configured settings path:

1. The absolute path in `JOB_APPLICATION_MANAGER_SETTINGS`, when that environment variable is set.
2. `$XDG_CONFIG_HOME/job-application-manager/settings.md`, when `XDG_CONFIG_HOME` is set.
3. `$HOME/.config/job-application-manager/settings.md`.

The file is Markdown with YAML frontmatter:

```yaml
---
schema_version: 1
data_store: "/absolute/path/to/job-search-data"
---
```

`data_store` must be an absolute path to an accessible directory. Do not infer a store by scanning the filesystem, and do not fall back to a path embedded in this skill. Use `<data-store>/settings.md` for the project settings described in [project schema](project-schema.md); the two settings files have different purposes.

If the per-user settings file is absent, malformed, or points to an unavailable directory, report the resolved settings path and the exact problem. Permit an explicit configuration repair, but do not initialize or modify job-search records until the data store resolves.
