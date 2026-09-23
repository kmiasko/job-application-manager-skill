#!/usr/bin/env python3
"""Preview and explicitly apply safe Google Contacts merges."""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any

PEOPLE = "https://people.googleapis.com/v1"
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPE = "https://www.googleapis.com/auth/contacts"
PERSON_FIELDS = "names,emailAddresses,phoneNumbers,organizations,metadata"


class ContactError(Exception):
    pass


class AuthorizationRequired(ContactError):
    pass


def config_dir() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "job-application-manager" / "google-contacts"


def credential_paths() -> tuple[Path, Path]:
    root = config_dir()
    return root / "client-secrets.json", root / "token.json"


def secure_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    temporary = path.with_suffix(path.suffix + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2)
            handle.write("\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ContactError(f"Expected a JSON object in {path}")
    return value


def normalize_email(value: str | None) -> str | None:
    value = value.strip().lower() if isinstance(value, str) else ""
    return value or None


def normalize_phone(value: str | None) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    international = value.startswith("+") or value.startswith("00")
    digits = "".join(char for char in value if char.isdigit())
    if value.startswith("00"):
        digits = digits[2:]
    return ("+" if international else "") + digits if digits else None


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None,
                 data: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(data).encode() if data is not None else None
    all_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        all_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=all_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read()).get("error", {}).get("message")
        except Exception:
            detail = None
        if exc.code in (401, 403):
            raise AuthorizationRequired(detail or "Google authorization is missing or expired") from None
        raise ContactError(detail or f"Google API returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ContactError(f"Network request failed: {exc}") from None
    if not payload:
        return {}
    try:
        result = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ContactError("Google returned an invalid JSON response") from exc
    return result


def oauth_client() -> dict[str, Any]:
    client_path, _ = credential_paths()
    try:
        root = load_json(client_path)
        client = root.get("installed") or root.get("web")
        if not isinstance(client, dict) or not client.get("client_id"):
            raise ContactError("OAuth client file has no installed client configuration")
        return client
    except FileNotFoundError:
        raise AuthorizationRequired("Google Contacts authorization has not been configured") from None


def token_request(fields: dict[str, str]) -> dict[str, Any]:
    encoded = urllib.parse.urlencode(fields).encode()
    request = urllib.request.Request(TOKEN_URL, data=encoded, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        raise AuthorizationRequired("Google Contacts authorization could not be refreshed") from exc


def access_token() -> str:
    _, token_path = credential_paths()
    try:
        token = load_json(token_path)
    except (FileNotFoundError, json.JSONDecodeError):
        raise AuthorizationRequired("Google Contacts authorization is required") from None
    if token.get("access_token") and float(token.get("expires_at", 0)) > time.time() + 60:
        return str(token["access_token"])
    refresh = token.get("refresh_token")
    if not refresh:
        raise AuthorizationRequired("Google Contacts authorization is expired")
    client = oauth_client()
    refreshed = token_request({
        "client_id": client["client_id"],
        "client_secret": client.get("client_secret", ""),
        "refresh_token": refresh,
        "grant_type": "refresh_token",
    })
    if not refreshed.get("access_token"):
        raise AuthorizationRequired("Google Contacts authorization could not be refreshed")
    token.update(refreshed)
    token["refresh_token"] = refresh
    token["expires_at"] = time.time() + int(refreshed.get("expires_in", 3600))
    secure_write(token_path, token)
    return str(token["access_token"])


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token()}"}


def list_contacts() -> list[dict[str, Any]]:
    contacts: list[dict[str, Any]] = []
    page_token = None
    while True:
        query = {"personFields": PERSON_FIELDS, "pageSize": "1000"}
        if page_token:
            query["pageToken"] = page_token
        result = request_json(f"{PEOPLE}/people/me/connections?{urllib.parse.urlencode(query)}",
                              headers=auth_headers())
        contacts.extend(item for item in result.get("connections", []) if isinstance(item, dict))
        page_token = result.get("nextPageToken")
        if not page_token:
            return contacts


def get_contact(resource_name: str) -> dict[str, Any] | None:
    safe_name = urllib.parse.quote(resource_name, safe="/")
    try:
        return request_json(f"{PEOPLE}/{safe_name}?{urllib.parse.urlencode({'personFields': PERSON_FIELDS})}",
                            headers=auth_headers())
    except ContactError as exc:
        if "not found" in str(exc).lower():
            return None
        raise


def values(person: dict[str, Any], field: str) -> list[str]:
    return [str(item.get("value", "")) for item in person.get(field, []) if isinstance(item, dict)]


def find_match(data: dict[str, Any], contacts: list[dict[str, Any]], stored: dict[str, Any] | None) -> tuple[dict[str, Any] | None, list[str]]:
    email, phone = normalize_email(data.get("email")), normalize_phone(data.get("phone"))
    if stored is not None:
        return stored, []
    email_matches = {p.get("resourceName") for p in contacts if email and email in {normalize_email(v) for v in values(p, "emailAddresses")}}
    phone_matches = {p.get("resourceName") for p in contacts if phone and phone in {normalize_phone(v) for v in values(p, "phoneNumbers")}}
    email_matches.discard(None)
    phone_matches.discard(None)
    combined = email_matches | phone_matches
    if len(combined) > 1:
        return None, sorted(str(item) for item in combined)
    if combined:
        name = next(iter(combined))
        return next(p for p in contacts if p.get("resourceName") == name), []
    return None, []


def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    clean = {key: data.get(key) for key in ("name", "email", "phone", "position", "company", "google_contact_resource_name")}
    for key in ("name", "company"):
        if not isinstance(clean[key], str) or not clean[key].strip():
            raise ContactError(f"Input field '{key}' is required")
        clean[key] = clean[key].strip()
    clean["email"] = normalize_email(clean.get("email"))
    clean["phone"] = normalize_phone(clean.get("phone"))
    if not clean["email"] and not clean["phone"]:
        raise ContactError("At least one of email or phone is required")
    for key in ("position", "google_contact_resource_name"):
        clean[key] = clean[key].strip() if isinstance(clean[key], str) and clean[key].strip() else None
    return clean


def merge_contact(person: dict[str, Any] | None, data: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    merged = json.loads(json.dumps(person or {}))
    changes: list[dict[str, Any]] = []
    update_fields: list[str] = []
    names = merged.setdefault("names", [])
    if not any(str(n.get("displayName", "")).strip() for n in names if isinstance(n, dict)):
        names.append({"displayName": data["name"]})
        changes.append({"field": "name", "action": "set", "value": data["name"]})
        update_fields.append("names")
    for source, field, kind in (("email", "emailAddresses", "work"), ("phone", "phoneNumbers", "work")):
        normalizer = normalize_email if source == "email" else normalize_phone
        desired = normalizer(data.get(source))
        if desired and desired not in {normalizer(v) for v in values(merged, field)}:
            merged.setdefault(field, []).append({"value": desired, "type": kind})
            changes.append({"field": source, "action": "append", "value": desired, "type": kind})
            update_fields.append(field)
    organizations = merged.setdefault("organizations", [])
    company_key = data["company"].strip().casefold()
    organization = next((o for o in organizations if isinstance(o, dict) and str(o.get("name", "")).strip().casefold() == company_key), None)
    if organization is None:
        organization = {"name": data["company"]}
        if data.get("position"):
            organization["title"] = data["position"]
        organizations.append(organization)
        changes.append({"field": "organization", "action": "append", "value": organization.copy()})
        update_fields.append("organizations")
    elif data.get("position") and organization.get("title") != data["position"]:
        previous = organization.get("title")
        organization["title"] = data["position"]
        changes.append({"field": "organization.title", "action": "set", "company": data["company"], "before": previous, "value": data["position"]})
        update_fields.append("organizations")
    return merged, changes, sorted(set(update_fields))


def fingerprint(person: dict[str, Any] | None) -> str | None:
    if person is None:
        return None
    return hashlib.sha256(json.dumps(person, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def plan_digest(plan: dict[str, Any]) -> str:
    core = {key: value for key, value in plan.items() if key not in ("plan_digest", "generated_at")}
    return hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def compute_plan(data: dict[str, Any]) -> dict[str, Any]:
    stored_name = data.get("google_contact_resource_name")
    stored = get_contact(stored_name) if stored_name else None
    contacts = list_contacts()
    person, ambiguous = find_match(data, contacts, stored)
    if ambiguous:
        plan = {"status": "ambiguous", "input": data, "matching_resource_names": ambiguous,
                "operation": None, "changes": []}
    else:
        merged, changes, update_fields = merge_contact(person, data)
        operation = "update" if person and changes else "noop" if person else "create"
        plan = {"status": operation, "input": data, "resource_name": person.get("resourceName") if person else None,
                "remote_fingerprint": fingerprint(person), "operation": operation, "changes": changes,
                "update_fields": update_fields, "merged_contact": merged}
    plan["plan_digest"] = plan_digest(plan)
    return plan


def authorize(client_secrets: Path) -> dict[str, Any]:
    source = load_json(client_secrets)
    client = source.get("installed") or source.get("web")
    if not isinstance(client, dict) or not client.get("client_id"):
        raise ContactError("Client secrets must contain an installed OAuth client")
    client_path, token_path = credential_paths()
    secure_write(client_path, source)
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(32)
    result: dict[str, str] = {}

    class Callback(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({key: values[0] for key, values in query.items() if values})
            body = b"Authorization received. You may close this window."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: Any) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Callback)
    redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect_uri, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
    })
    print(json.dumps({"status": "authorization-required", "authorization_url": url, "message": "Open the URL to authorize Google Contacts."}))
    webbrowser.open(url)
    server.timeout = 300
    server.handle_request()
    server.server_close()
    if not result.get("code") or not secrets.compare_digest(result.get("state", ""), state):
        raise AuthorizationRequired("OAuth callback was missing or failed state validation")
    token = token_request({"client_id": client["client_id"], "client_secret": client.get("client_secret", ""),
                           "code": result["code"], "code_verifier": verifier, "redirect_uri": redirect_uri,
                           "grant_type": "authorization_code"})
    if not token.get("access_token"):
        raise AuthorizationRequired("Google did not return an access token")
    token["expires_at"] = time.time() + int(token.get("expires_in", 3600))
    secure_write(token_path, token)
    return {"status": "authorized"}


def preview(input_path: Path, output_path: Path) -> dict[str, Any]:
    plan = compute_plan(validate_input(load_json(input_path)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2)
        handle.write("\n")
    return {key: value for key, value in plan.items() if key != "merged_contact"}


def apply_plan(path: Path, confirmed: bool) -> dict[str, Any]:
    if not confirmed:
        raise ContactError("Apply requires --confirmed")
    saved = load_json(path)
    if saved.get("plan_digest") != plan_digest(saved):
        return {"status": "stale-preview", "message": "The preview file was modified"}
    if saved.get("status") not in ("create", "update"):
        return {"status": saved.get("status", "failed"), "message": "The preview contains no writable operation"}
    fresh = compute_plan(validate_input(saved.get("input", {})))
    comparable = ("status", "resource_name", "remote_fingerprint", "changes", "update_fields", "merged_contact")
    if any(saved.get(key) != fresh.get(key) for key in comparable):
        return {"status": "stale-preview", "message": "The remote contact or proposed operation changed; create a new preview"}
    if fresh["status"] == "create":
        result = request_json(f"{PEOPLE}/people:createContact", method="POST", headers=auth_headers(), data=fresh["merged_contact"])
    else:
        name = urllib.parse.quote(str(fresh["resource_name"]), safe="/")
        query = urllib.parse.urlencode({"updatePersonFields": ",".join(fresh["update_fields"]), "personFields": PERSON_FIELDS})
        result = request_json(f"{PEOPLE}/{name}:updateContact?{query}", method="PATCH", headers=auth_headers(), data=fresh["merged_contact"])
    return {"status": fresh["status"], "resource_name": result.get("resourceName") or fresh.get("resource_name"), "changes": fresh["changes"]}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    auth = commands.add_parser("authorize")
    auth.add_argument("--client-secrets", type=Path, required=True)
    show = commands.add_parser("preview")
    show.add_argument("--input", type=Path, required=True)
    show.add_argument("--output", type=Path, required=True)
    apply = commands.add_parser("apply")
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--confirmed", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "authorize":
            result = authorize(args.client_secrets)
        elif args.command == "preview":
            result = preview(args.input, args.output)
        else:
            result = apply_plan(args.plan, args.confirmed)
    except AuthorizationRequired as exc:
        result = {"status": "authorization-required", "message": str(exc)}
    except (ContactError, OSError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "message": str(exc)}
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") not in ("failed", "authorization-required", "stale-preview") else 1


if __name__ == "__main__":
    sys.exit(main())
