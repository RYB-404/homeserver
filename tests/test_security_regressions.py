import unittest

import hashlib

from app import app, hash_password, verify_password


class SecurityRegressionTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def assert_requires_auth(self, response):
        self.assertIn(response.status_code, {302, 401, 403})

    def login_as(self, role):
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True
            sess["username"] = f"{role}_user"
            sess["role"] = role
            sess["last_active"] = 9999999999

    def test_file_content_requires_auth(self):
        response = self.client.get("/api/files/content", query_string={"path": "README.md"})
        self.assert_requires_auth(response)

    def test_docker_api_requires_auth(self):
        response = self.client.get("/api/docker/containers")
        self.assert_requires_auth(response)

    def test_system_api_requires_auth(self):
        response = self.client.get("/api/system")
        self.assert_requires_auth(response)

    def test_dashboard_apps_requires_auth(self):
        response = self.client.get("/api/dashboard/apps")
        self.assert_requires_auth(response)

    def test_health_requires_auth(self):
        response = self.client.get("/api/health")
        self.assert_requires_auth(response)

    def test_health_returns_mode_and_capabilities_for_logged_in_user(self):
        self.login_as("owner")
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data["mode"], {"safe", "host-control"})
        self.assertIn("capabilities", data)
        self.assertIn("docker", data["capabilities"])
        self.assertIn("host_filesystem", data["capabilities"])

    def test_storage_plan_returns_homeserver_paths(self):
        self.login_as("owner")
        response = self.client.get("/api/storage/plan")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        paths = {item["id"]: item["path"] for item in data["paths"]}
        self.assertEqual(paths["photos"], "/mnt/photos/immich")
        self.assertEqual(paths["media"], "/mnt/media")
        self.assertEqual(paths["apps"], "/opt/homeserver")

    def test_mobile_backup_ping_requires_auth(self):
        response = self.client.get("/api/mobile-backup/ping")
        self.assert_requires_auth(response)

    def test_mobile_backup_upload_requires_auth(self):
        response = self.client.post("/api/mobile-backup/upload")
        self.assert_requires_auth(response)

    def test_mobile_key_does_not_bypass_general_auth(self):
        response = self.client.get(
            "/api/files/content",
            query_string={"path": "README.md"},
            headers={"X-Mobile-Key": "EkaBackupSync_2024_Secret"},
        )
        self.assert_requires_auth(response)

    def test_untrusted_origin_does_not_receive_cors_credentials(self):
        response = self.client.get("/login", headers={"Origin": "https://attacker.example"})
        self.assertNotEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "https://attacker.example",
        )

    def test_password_hashing_uses_salted_kdf_and_accepts_legacy_hashes(self):
        password_hash = hash_password("correct horse battery staple")
        self.assertTrue(password_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("wrong", password_hash))

        legacy_hash = hashlib.sha256("admin".encode()).hexdigest()
        self.assertTrue(verify_password("admin", legacy_hash))

    def test_readonly_cannot_change_security_config(self):
        self.login_as("readonly")
        response = self.client.post("/api/security/config", json={"require_auth": False})
        self.assertEqual(response.status_code, 403)

    def test_readonly_cannot_run_panel_docker_action(self):
        self.login_as("readonly")
        response = self.client.post(
            "/api/panel_docker/action",
            json={"name": "example", "action": "restart"},
        )
        self.assertEqual(response.status_code, 403)

    def test_readonly_cannot_create_lxd_container(self):
        self.login_as("readonly")
        response = self.client.post("/api/lxd/create", json={"name": "example"})
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
