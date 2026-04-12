from datetime import datetime, timedelta, timezone
import unittest

from src.application.use_cases.manage_profiles import ManageProfilesUseCase
from src.domain.entities.auth_profile import AuthConfig, AuthCredentials, AuthProfile
from src.domain.interfaces.auth_connector import IAuthConnector
from src.domain.interfaces.auth_profile_repository import IAuthProfileRepository


class _InMemoryProfileRepository(IAuthProfileRepository):
    def __init__(self, profiles: list[AuthProfile] | None = None) -> None:
        self._profiles = {profile.profile_id: profile for profile in profiles or []}

    def list_profiles(self) -> list[AuthProfile]:
        return list(self._profiles.values())

    def get_profile(self, profile_id: str) -> AuthProfile | None:
        return self._profiles.get(profile_id)

    def save_profile(self, profile: AuthProfile) -> AuthProfile:
        self._profiles[profile.profile_id] = profile
        return profile

    def delete_profile(self, profile_id: str) -> None:
        self._profiles.pop(profile_id, None)


class _FakeConnector(IAuthConnector):
    def __init__(self, credentials: AuthCredentials) -> None:
        self.credentials = credentials
        self.calls = 0

    async def fetch_credentials(self, profile: AuthProfile) -> AuthCredentials:
        self.calls += 1
        return self.credentials


class ManageProfilesUseCaseTest(unittest.IsolatedAsyncioTestCase):
    async def test_resolve_auth_profile_reuses_cached_credentials_when_still_valid(self) -> None:
        cached_credentials = AuthCredentials(
            token="cached-token",
            cookies={"session": "cached-cookie"},
            expiry=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        repo = _InMemoryProfileRepository(
            [
                AuthProfile(
                    profile_id="staging",
                    name="Staging",
                    auth_config=AuthConfig(url="https://auth.example.com/token"),
                    last_credentials=cached_credentials,
                )
            ]
        )
        connector = _FakeConnector(
            AuthCredentials(token="fresh-token", cookies={"session": "fresh-cookie"})
        )
        use_case = ManageProfilesUseCase(repo, connector)

        resolved = await use_case.resolve_auth_profile("staging")

        self.assertEqual("cached-token", resolved.access_token)
        self.assertEqual({"session": "cached-cookie"}, resolved.cookies)
        self.assertEqual(0, connector.calls)

    async def test_resolve_auth_profile_refreshes_and_persists_expired_credentials(self) -> None:
        expired_credentials = AuthCredentials(
            token="expired-token",
            expiry=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        fresh_credentials = AuthCredentials(
            token="fresh-token",
            cookies={"session": "fresh-cookie"},
            expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        repo = _InMemoryProfileRepository(
            [
                AuthProfile(
                    profile_id="staging",
                    name="Staging",
                    auth_config=AuthConfig(url="https://auth.example.com/token"),
                    last_credentials=expired_credentials,
                )
            ]
        )
        connector = _FakeConnector(fresh_credentials)
        use_case = ManageProfilesUseCase(repo, connector)

        resolved = await use_case.resolve_auth_profile("staging")

        self.assertEqual("fresh-token", resolved.access_token)
        self.assertEqual({"session": "fresh-cookie"}, resolved.cookies)
        self.assertEqual(1, connector.calls)
        self.assertEqual("fresh-token", repo.get_profile("staging").last_credentials.token)
