# Google Contacts synchronization

Read this reference when an interviewer gains or changes an email address or phone number. Synchronization is one-way from the interviewer record to Google Contacts; it searches Contacts, not Other Contacts, and never copies remote fields into Markdown.

## Local-first workflow

1. Save the supplied interviewer data in the interview file first. Map a supplied email to `contact_email` and a supplied phone to `contact_number`; preserve `role`, `contact_details`, unknown fields, and manual content.
2. Build a private temporary JSON input containing `name`, optional `email`, optional `phone`, optional `position`, `company`, and optional `google_contact_resource_name`. At least one of email or phone is required. Do not put this temporary input or the generated plan in the data store, Calendar, history, or logs.
3. Run `python3 scripts/google_contacts.py preview --input <input.json> --output <plan.json>`. If it returns `authorization-required`, set `google_contact_sync_state: blocked` and tell the user to run `python3 scripts/google_contacts.py authorize --client-secrets <downloaded-client-secrets.json>`. Credentials remain in the user's XDG configuration directory.
4. For `create` or `update`, show the operation and every field-level change exactly as returned. Set the local state to `previewed` and obtain explicit confirmation that enumerates every contact operation in the preview. Then run `python3 scripts/google_contacts.py apply --plan <plan.json> --confirmed`.
5. A `noop` needs no confirmation. Record `google_contact_sync_state: noop`, the returned resource name when present, and `google_contact_synced_at` with the current explicit-offset timestamp.
6. For successful `create` or `update`, record `google_contact_sync_state: synced`, the returned resource name, and `google_contact_synced_at`. Explain once that Android receives the contact only when it uses the same Google account and Google Contacts sync is enabled.
7. For `ambiguous`, make no external write and set the state to `blocked`. For `stale-preview` or `failed`, make no retry or external write without a fresh preview; set the state to `failed` and report the structured error. Local interview and Calendar changes remain intact.

Delete temporary inputs and plans after the operation or when abandoning it. Never expose or store OAuth client secrets, access tokens, refresh tokens, or authorization codes in the repository, data store, Calendar, previews, history, or messages.

## Matching and merge behavior

The helper matches exact normalized email addresses and phone numbers. Email normalization trims and lowercases only. Phone normalization removes formatting and converts an initial `00` to `+`; it never infers a country code. A stored Google resource name is preferred on later synchronizations. Multiple matches, or email and phone resolving to different contacts, are ambiguous and cause no write.

The safe merge appends missing work email and phone values, fills an absent name while preserving an existing non-empty name, and adds or updates the organization entry for the offer company with the offer position as title. It preserves all unrelated names, emails, phone numbers, organizations, notes, memberships, and other fields.
