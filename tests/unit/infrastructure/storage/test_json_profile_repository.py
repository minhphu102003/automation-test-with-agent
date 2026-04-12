from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from src.domain.entities.auth_profile import AuthConfig, AuthCredentials, AuthMapping, AuthProfile
from src.infrastructure.storage.json_profile_repository import JsonAuthProfileRepository


class JsonAuthProfileRepositoryTest(unittest.TestCase):
    def test_save_and_load_profile_round_trips_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonAuthProfileRepository(str(Path(temp_dir) / "profiles.json"))
            profile = AuthProfile(
                profile_id="staging",
                name="Staging",
                auth_config=AuthConfig(
                    url="https://auth.example.com/token",
                    method="POST",
                    body={"username": "qa"},
                    headers={"X-App": "browser-testing"},
                    mapping=AuthMapping(
                        token_path="data.token",
                        cookies_path="data.cookies",
                        expiry_path="data.expiry",
                    ),
                    token_key="access_token",
                ),
                last_credentials=AuthCredentials(
                    token="abc123",
                    cookies={"session": "cookie-value"},
                    expiry=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc),
                ),
            )

            repo.save_profile(profile)
            loaded = repo.get_profile("staging")

            self.assertIsNotNone(loaded)
            self.assertEqual("Staging", loaded.name)
            self.assertEqual("data.token", loaded.auth_config.mapping.token_path)
            self.assertEqual({"session": "cookie-value"}, loaded.last_credentials.cookies)
            self.assertEqual(profile.last_credentials.expiry, loaded.last_credentials.expiry)
