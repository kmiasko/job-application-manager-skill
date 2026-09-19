# Profile workflow

Read for explicit profile initialization/repair, ingestion, analysis, fit assessment, or candidate-specific interview preparation. Ordinary offer and local record operations do not load this reference.

## Validate evidence for the task

Validate only the sources and derived material the requested assessment or preparation will use. Check source readability, configured source identity where applicable, and matching fingerprints before trusting derived claims. Compute hashes locally and return discrepancies, not entire profile bodies: CV fingerprints cover source bytes; LinkedIn fingerprints cover the normalized captured content. Reuse the capture's normalization convention; if it is unknown, report unverifiable freshness rather than declaring a match. Do not fetch LinkedIn again without a refresh request.

An assessment using only supplied CV evidence need not require LinkedIn, profile analysis, or interview stories. When using `profile-analysis.md`, verify its recorded fingerprints against the underlying sources; when using interview stories, check their cited evidence. Missing or stale evidence blocks only claims that depend on it. State the limitation and request the needed source or explicit repair; continue independent offer capture, logistics, company briefing, and technical preparation. Never infer candidate experience to fill gaps.

`setup_complete` summarizes explicit profile setup, not permission to perform other workflows. Calendar settings and authorization are checked only for requested Calendar operations.

## Initialize

For an explicit initialization request, if `settings.md` is absent, create it using the settings schema in [project schema](project-schema.md), preserve existing offer records, explain which profile values must be filled, and stop the initialization portion. Independent work in the same request can continue.

For full profile setup, treat setup as incomplete when a required profile source setting is missing, either normalized source is missing or unreadable, source identity or fingerprints disagree with the analysis, `profile-analysis.md` is absent, or `knowledge/interview-stories.md` is absent. This affects full profile setup and dependent evidence only.

Full profile setup requires these non-placeholder source settings:

- `cv_file`
- `linkedin_profile_url`

Use `Europe/Warsaw` and Polish when timezone or analysis/preparation language settings are absent. Validate an explicitly supplied value when using it. Calendar ID is not a profile requirement.

Routing configuration is optional and does not affect profile completeness. Before delegation, validate the current runtime's configured fields as described in [agent routing](agent-routing.md). Unsupported foreign-runtime or legacy values use current-runtime defaults with an explicit fallback notice; invalid settings for the current runtime permit only repair.

## Capture sources

Read the configured CV file using an appropriate document extractor. Record a SHA-256 fingerprint of its source bytes, its absolute source path, and capture time in `cv.md` frontmatter.

Open the configured LinkedIn URL in an available browser session. If authentication or verification is required, pause for the user to complete it interactively, then continue. Never request or store credentials, cookies, or tokens. Record a SHA-256 fingerprint of the normalized captured content, the profile URL, and capture time in `linkedin.md` frontmatter.

Both normalized files must faithfully organize the source facts and preserve uncertainties. Do not improve prose in a way that strengthens, invents, or resolves claims. Clearly mark content that was inaccessible. Setup cannot complete unless both sources are captured well enough to analyze.

## Analyze

Create `profile-analysis.md` in Polish with:

- positioning summary and plausible target roles;
- seniority evidence;
- technical and domain strengths;
- leadership and communication evidence;
- measurable achievements;
- weak, unsupported, or ambiguous areas;
- CV and LinkedIn inconsistencies;
- concrete profile-improvement recommendations;
- a `User-provided additions` section for later explicit self-reported evidence.

Record both source fingerprints in frontmatter so setup verification can detect staleness. Do not treat inferred facts as evidence.

Create `knowledge/interview-stories.md` in Polish during the same operation. Build reusable STAR-style stories only from traceable profile evidence. Cite the relevant normalized-source section. When a complete story needs facts not present in either source, write focused questions for the user instead of filling gaps.

After every full-profile output exists and fingerprints agree, set `setup_complete: true` in `settings.md`. Later profile-dependent tasks validate their needed evidence as described above; other invocations do not recheck setup.

## Source changes

If a profile operation detects a changed source identity or fingerprint, set `setup_complete: false` and stop relying on affected derived claims. Continue independent requested work. On explicit reanalysis, overwrite `cv.md`, `linkedin.md`, `profile-analysis.md`, and the generated portions of `knowledge/interview-stories.md`; do not retain profile versions. Preserve `User-provided additions` and user-owned notes.
