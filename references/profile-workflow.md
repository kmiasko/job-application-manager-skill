# Profile workflow

Read this reference for initialization, settings repair, CV or LinkedIn ingestion, profile analysis, and profile-source changes.

## Initialize

If `settings.md` is absent, create only that file using the settings schema in [project schema](project-schema.md). Keep the recommended defaults, leave required values as visible placeholders, explain what the user must fill, and stop. Do not create any other project file in that operation.

Treat setup as incomplete when any required setting is missing, either normalized source is missing or unreadable, a source fingerprint differs from the fingerprint used by the analysis, `profile-analysis.md` is absent, or `knowledge/interview-stories.md` is absent. While incomplete, permit only initialization, profile ingestion or analysis, settings repair, and setup diagnosis.

Require these non-placeholder settings before analysis:

- `cv_file`
- `linkedin_profile_url`
- `google_calendar_id`
- `timezone`
- `technical_analysis_language`
- `default_interview_language`

Routing configuration is optional and does not affect profile completeness. Before delegation, validate the current runtime's configured fields as described in [agent routing](agent-routing.md). Unsupported foreign-runtime or legacy values use current-runtime defaults with an explicit fallback notice; invalid settings for the current runtime permit only repair.

Validate the Calendar ID's presence, not live authorization. Test authorization only immediately before the first requested Calendar operation.

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

After every output exists and fingerprints agree, set `setup_complete: true` in `settings.md`. Verify these conditions on every later skill invocation rather than trusting the flag.

## Source changes

If the configured source changes or its fingerprint no longer matches, set `setup_complete: false` and permit only setup or repair operations. On explicit reanalysis, overwrite `cv.md`, `linkedin.md`, `profile-analysis.md`, and the generated portions of `knowledge/interview-stories.md`; do not retain profile versions. Preserve `User-provided additions` and user-owned notes.
