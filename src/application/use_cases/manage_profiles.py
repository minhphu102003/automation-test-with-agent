from __future__ import annotations

import uuid
from typing import Any

from src.domain.entities.auth_profile import AuthConfig, AuthCredentials, AuthProfile, ResolvedAuthProfile
from src.domain.exceptions.base import DomainException, NotFoundException
from src.domain.interfaces.auth_connector import IAuthConnector
from src.domain.interfaces.auth_profile_repository import IAuthProfileRepository


class ManageAuthProfilesUseCase:
    def __init__(
        self,
        repository: IAuthProfileRepository,
        connector: IAuthConnector,
    ) -> None:
        self.repository = repository
        self.connector = connector

    def list_profiles(self) -> list[AuthProfile]:
        return self.repository.list_profiles()

    def get_profile(self, profile_id: str) -> AuthProfile:
        profile = self.repository.get_profile(profile_id)
        if profile is None:
            raise NotFoundException(f"Auth profile '{profile_id}' was not found")
        return profile

    def create_profile(self, payload: AuthProfile | dict[str, Any]) -> AuthProfile:
        if isinstance(payload, AuthProfile):
            profile = payload
        else:
            profile = AuthProfile(
                profile_id=str(payload.get("profile_id") or uuid.uuid4()),
                name=self._require_name(payload.get("name")),
                auth_config=self._build_auth_config(payload.get("auth_config")),
                last_credentials=AuthCredentials.from_dict(payload.get("last_credentials")),
            )

        if self.repository.get_profile(profile.profile_id) is not None:
            raise DomainException(f"Auth profile '{profile.profile_id}' already exists")
        return self.repository.save_profile(profile)

    def update_profile(self, profile_id: str, payload: AuthProfile | dict[str, Any]) -> AuthProfile:
        existing = self.get_profile(profile_id)

        if isinstance(payload, AuthProfile):
            profile = payload
            return self.repository.save_profile(
                AuthProfile(
                    profile_id=profile_id,
                    name=profile.name,
                    auth_config=profile.auth_config,
                    last_credentials=profile.last_credentials,
                )
            )

        return self.repository.save_profile(
            AuthProfile(
                profile_id=profile_id,
                name=self._require_name(payload.get("name", existing.name)),
                auth_config=self._build_auth_config(payload.get("auth_config"), fallback=existing.auth_config),
                last_credentials=(
                    AuthCredentials.from_dict(payload.get("last_credentials"))
                    if payload.get("last_credentials") is not None
                    else existing.last_credentials
                ),
            )
        )

    def delete_profile(self, profile_id: str) -> None:
        if self.repository.get_profile(profile_id) is None:
            raise NotFoundException(f"Auth profile '{profile_id}' was not found")
        self.repository.delete_profile(profile_id)

    async def resolve_auth_profile(self, profile_id: str) -> ResolvedAuthProfile:
        profile = self.get_profile(profile_id)
        credentials = profile.last_credentials

        if not credentials.is_usable():
            if profile.auth_config.mode.lower() != "api":
                raise DomainException(
                    f"Auth profile '{profile_id}' requires stored credentials for mode "
                    f"'{profile.auth_config.mode}'"
                )
            if not profile.auth_config.url:
                raise DomainException(
                    f"Auth profile '{profile_id}' has no auth URL configured for refresh"
                )
            credentials = await self.connector.fetch_credentials(profile)
            profile = self.repository.save_profile(profile.with_credentials(credentials))

        return ResolvedAuthProfile(
            profile_id=profile.profile_id,
            name=profile.name,
            url=profile.auth_config.metadata.get("app_url") or profile.auth_config.url or None,
            access_token=profile.last_credentials.token,
            cookies=profile.last_credentials.cookies,
            token_key=profile.auth_config.token_key,
            expiry=profile.last_credentials.expiry,
        )

    async def resolve_runtime_auth(self, profile_id: str) -> dict[str, Any]:
        resolved = await self.resolve_auth_profile(profile_id)
        return {
            "profile_id": resolved.profile_id,
            "profile_name": resolved.name,
            "url": resolved.url,
            "access_token": resolved.access_token,
            "cookies": resolved.cookies or None,
            "token_key": resolved.token_key,
            "expiry": resolved.expiry.isoformat() if resolved.expiry else None,
        }

    def _build_auth_config(
        self,
        payload: dict[str, Any] | None,
        fallback: AuthConfig | None = None,
    ) -> AuthConfig:
        if payload is None and fallback is not None:
            return fallback
        auth_config = AuthConfig.from_dict(payload)
        if not auth_config.url:
            raise DomainException("auth_config.url is required")
        if auth_config.mode.lower() not in {"api", "ui"}:
            raise DomainException("auth_config.auth_type must be either 'api' or 'ui'")
        return auth_config

    def _require_name(self, name: Any) -> str:
        value = str(name or "").strip()
        if not value:
            raise DomainException("Profile name is required")
        return value


ManageProfilesUseCase = ManageAuthProfilesUseCase
