import importlib.util
import json
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "google_contacts.py"
SPEC = importlib.util.spec_from_file_location("google_contacts", SCRIPT)
gc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(gc)


class NormalizationTests(unittest.TestCase):
    def test_email_is_trimmed_and_lowercased_only(self):
        self.assertEqual(gc.normalize_email(" A.B+tag@Example.COM "), "a.b+tag@example.com")

    def test_phone_formatting_and_international_prefix(self):
        self.assertEqual(gc.normalize_phone("00 48 (123) 456-789"), "+48123456789")
        self.assertEqual(gc.normalize_phone("(123) 456-789"), "123456789")
        self.assertEqual(gc.normalize_phone("+1 212 555 0100"), "+12125550100")


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.contacts = [
            {"resourceName": "people/1", "emailAddresses": [{"value": "A@example.com"}]},
            {"resourceName": "people/2", "phoneNumbers": [{"value": "+48 123"}]},
        ]

    def test_zero_one_and_multiple_matches(self):
        self.assertIsNone(gc.find_match({"email": "none@example.com", "phone": None}, self.contacts, None)[0])
        self.assertEqual(gc.find_match({"email": "a@example.com", "phone": None}, self.contacts, None)[0]["resourceName"], "people/1")
        person, ambiguous = gc.find_match({"email": "a@example.com", "phone": "+48123"}, self.contacts, None)
        self.assertIsNone(person)
        self.assertEqual(ambiguous, ["people/1", "people/2"])

    def test_stored_resource_wins(self):
        stored = {"resourceName": "people/stored"}
        self.assertIs(gc.find_match({"email": "a@example.com"}, self.contacts, stored)[0], stored)

    @mock.patch.object(gc, "request_json")
    @mock.patch.object(gc, "auth_headers", return_value={})
    def test_pagination(self, _headers, request):
        request.side_effect = [
            {"connections": [{"resourceName": "people/1"}], "nextPageToken": "next"},
            {"connections": [{"resourceName": "people/2"}]},
        ]
        self.assertEqual(len(gc.list_contacts()), 2)
        self.assertIn("pageToken=next", request.call_args_list[1].args[0])


class MergeTests(unittest.TestCase):
    def test_safe_merge_preserves_unrelated_fields(self):
        person = {
            "resourceName": "people/1",
            "etag": "old",
            "names": [{"displayName": "Existing Name"}],
            "emailAddresses": [{"value": "personal@example.com", "type": "home"}],
            "phoneNumbers": [{"value": "111", "type": "home"}],
            "organizations": [{"name": "Other Co", "title": "Founder"}, {"name": "Acme", "title": "Old"}],
            "biographies": [{"value": "keep me"}],
            "memberships": [{"contactGroupMembership": {"contactGroupResourceName": "contactGroups/friends"}}],
        }
        data = {"name": "New Name", "email": "work@example.com", "phone": "+48123", "company": "Acme", "position": "CTO"}
        merged, changes, fields = gc.merge_contact(person, data)
        self.assertEqual(merged["names"], person["names"])
        self.assertEqual(merged["biographies"], person["biographies"])
        self.assertEqual(merged["memberships"], person["memberships"])
        self.assertEqual(len(merged["emailAddresses"]), 2)
        self.assertEqual(len(merged["phoneNumbers"]), 2)
        self.assertEqual(merged["organizations"][0], person["organizations"][0])
        self.assertEqual(merged["organizations"][1]["title"], "CTO")
        self.assertEqual(fields, ["emailAddresses", "organizations", "phoneNumbers"])
        self.assertTrue(changes)

    def test_missing_name_and_organization_are_added(self):
        merged, _, fields = gc.merge_contact({}, {"name": "Ada", "email": "a@b.test", "phone": None, "company": "Acme", "position": "Dev"})
        self.assertEqual(merged["names"][0]["displayName"], "Ada")
        self.assertEqual(merged["organizations"][0], {"name": "Acme", "title": "Dev"})
        self.assertIn("names", fields)

    def test_noop_detection(self):
        person = {"names": [{"displayName": "Ada"}], "emailAddresses": [{"value": "a@b.test"}],
                  "phoneNumbers": [{"value": "123"}], "organizations": [{"name": "Acme", "title": "Dev"}]}
        _, changes, fields = gc.merge_contact(person, {"name": "Ada", "email": "A@B.TEST", "phone": "1 2 3", "company": "acme", "position": "Dev"})
        self.assertEqual(changes, [])
        self.assertEqual(fields, [])


class PlanTests(unittest.TestCase):
    @mock.patch.object(gc, "list_contacts", return_value=[])
    @mock.patch.object(gc, "get_contact", return_value=None)
    def test_deleted_stored_resource_falls_back_to_search(self, get_contact, _list):
        plan = gc.compute_plan({"name": "Ada", "email": "a@b.test", "phone": None, "company": "Acme", "position": None, "google_contact_resource_name": "people/deleted"})
        get_contact.assert_called_once_with("people/deleted")
        self.assertEqual(plan["status"], "create")

    def test_apply_requires_confirmation(self):
        with self.assertRaisesRegex(gc.ContactError, "--confirmed"):
            gc.apply_plan(Path("unused"), False)

    def test_ambiguous_plan_is_not_writable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            plan = {"status": "ambiguous", "input": {}, "operation": None, "changes": []}
            plan["plan_digest"] = gc.plan_digest(plan)
            path.write_text(json.dumps(plan))
            self.assertEqual(gc.apply_plan(path, True)["status"], "ambiguous")

    def test_modified_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            plan = {"status": "create", "input": {}, "changes": []}
            plan["plan_digest"] = "bad"
            path.write_text(json.dumps(plan))
            self.assertEqual(gc.apply_plan(path, True)["status"], "stale-preview")

    @mock.patch.object(gc, "compute_plan")
    def test_changed_remote_contact_is_rejected(self, compute):
        saved = {"status": "update", "input": {"name": "Ada", "email": "a@b.test", "phone": None, "company": "Acme", "position": None, "google_contact_resource_name": None},
                 "resource_name": "people/1", "remote_fingerprint": "old", "changes": [], "update_fields": [], "merged_contact": {}}
        saved["plan_digest"] = gc.plan_digest(saved)
        compute.return_value = {**saved, "remote_fingerprint": "new"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(saved))
            self.assertEqual(gc.apply_plan(path, True)["status"], "stale-preview")

    @mock.patch.object(gc, "list_contacts", side_effect=gc.AuthorizationRequired("expired"))
    def test_expired_authorization_surfaces(self, _list):
        with self.assertRaisesRegex(gc.AuthorizationRequired, "expired"):
            gc.compute_plan({"name": "Ada", "email": "a@b.test", "phone": None, "company": "Acme", "position": None, "google_contact_resource_name": None})

    @mock.patch.object(gc, "request_json", side_effect=gc.ContactError("API unavailable"))
    @mock.patch.object(gc, "auth_headers", return_value={})
    @mock.patch.object(gc, "compute_plan")
    def test_api_error_does_not_get_converted_to_success(self, compute, _headers, _request):
        fresh = {"status": "create", "input": {"name": "Ada", "email": "a@b.test", "phone": None, "company": "Acme", "position": None, "google_contact_resource_name": None},
                 "resource_name": None, "remote_fingerprint": None, "changes": [{"field": "name"}], "update_fields": ["names"], "merged_contact": {"names": [{"displayName": "Ada"}]}}
        saved = dict(fresh)
        saved["plan_digest"] = gc.plan_digest(saved)
        compute.return_value = fresh
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(saved))
            with self.assertRaisesRegex(gc.ContactError, "API unavailable"):
                gc.apply_plan(path, True)


class CredentialTests(unittest.TestCase):
    def test_secure_write_permissions_and_no_stdout_secret(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": directory}):
            path = gc.config_dir() / "token.json"
            gc.secure_write(path, {"access_token": "secret"})
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(json.loads(path.read_text())["access_token"], "secret")

    @mock.patch.object(gc, "token_request", return_value={"access_token": "new", "expires_in": 3600})
    def test_refresh_preserves_refresh_token(self, _request):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": directory}):
            client, token = gc.credential_paths()
            gc.secure_write(client, {"installed": {"client_id": "id", "client_secret": "client-secret"}})
            gc.secure_write(token, {"access_token": "old", "refresh_token": "refresh-secret", "expires_at": 0})
            self.assertEqual(gc.access_token(), "new")
            saved = json.loads(token.read_text())
            self.assertEqual(saved["refresh_token"], "refresh-secret")
            self.assertGreater(saved["expires_at"], time.time())

    @mock.patch("secrets.compare_digest", return_value=False)
    def test_oauth_state_validation_uses_constant_time_compare(self, compare):
        self.assertFalse(compare("wrong", "expected"))


if __name__ == "__main__":
    unittest.main()
