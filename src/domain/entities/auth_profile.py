from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, "", 0):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    raise ValueError(f"Unsupported datetime value: {value!r}")


@dataclass(frozen=True, slots=True)
class AuthMapping:
    token_path: str | None = None
    cookies_path: str | None = None
    expiry_path: str | None = None

    @classmethod
    def from_value(cls, value: Any) -> "AuthMapping":
        if value in (None, "", {}):
            return cls()
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            return cls(token_path=value)
        if isinstance(value, dict):
            return cls(
                token_path=value.get("token") or value.get("token_path"),
                cookies_path=value.get("cookies") or value.get("cookies_path"),
                expiry_path=value.get("expiry") or value.get("expiry_path"),
            )
        raise ValueError(f"Unsupported auth mapping value: {value!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token_path,
            "cookies": self.cookies_path,
            "expiry": self.expiry_path,
        }


@dataclass(frozen=True, slots=True)
class AuthConfig:
    mode: str = "api"
    url: str = ""
    method: str = "POST"
    body: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    mapping: AuthMapping = field(default_factory=AuthMapping)
    token_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def auth_type(self) -> str:
        return self.mode

    @property
    def mapping_path(self) -> str | None:
        return self.mapping.token_path

    @property
    def expiry_mapping_path(self) -> str | None:
        return self.mapping.expiry_path

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AuthConfig":
        payload = data or {}
        raw_headers = payload.get("headers", payload.get("header", {})) or {}
        mapping = AuthMapping.from_value(payload.get("mapping") or payload.get("mapping_path"))
        expiry_mapping_path = payload.get("expiry_mapping_path")
        if expiry_mapping_path and not mapping.expiry_path:
            mapping = replace(mapping, expiry_path=expiry_mapping_path)

        return cls(
            mode=str(payload.get("auth_type", payload.get("mode", "api"))),
            url=str(payload.get("url", "")),
            method=str(payload.get("method", "POST")).upper(),
            body=dict(payload.get("body", {}) or {}),
            headers={str(key): str(value) for key, value in dict(raw_headers).items()},
            mapping=mapping,
            token_key=payload.get("token_key"),
            metadata=dict(payload.get("metadata", {}) or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "method": self.method,
            "body": self.body,
            "headers": self.headers,
            "mapping": self.mapping.to_dict(),
            "mapping_path": self.mapping.token_path,
            "expiry_mapping_path": self.mapping.expiry_path,
            "token_key": self.token_key,
            "mode": self.mode,
            "auth_type": self.mode,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class AuthCredentials:
    token: str | None = None
    cookies: dict[str, str] = field(default_factory=dict)
    expiry: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AuthCredentials":
        payload = data or {}
        return cls(
            token=payload.get("token"),
            cookies={str(key): str(value) for key, value in dict(payload.get("cookies", {}) or {}).items()},
            expiry=parse_datetime(payload.get("expiry")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "cookies": self.cookies,
            "expiry": self.expiry.astimezone(timezone.utc).isoformat() if self.expiry else None,
        }

    def is_usable(self, now: datetime | None = None) -> bool:
        if not self.token and not self.cookies:
            return False
        if self.expiry is None:
            return True
        reference_time = now or utc_now()
        expiry = self.expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return expiry > reference_time


LastCredentials = AuthCredentials


@dataclass(frozen=True, slots=True)
class AuthProfile:
    profile_id: str
    name: str
    auth_config: AuthConfig
    last_credentials: AuthCredentials = field(default_factory=AuthCredentials)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuthProfile":
        return cls(
            profile_id=str(data["profile_id"]),
            name=str(data["name"]),
            auth_config=AuthConfig.from_dict(data.get("auth_config")),
            last_credentials=AuthCredentials.from_dict(data.get("last_credentials")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "auth_config": self.auth_config.to_dict(),
            "last_credentials": self.last_credentials.to_dict(),
        }

    def with_credentials(self, credentials: AuthCredentials) -> "AuthProfile":
        return replace(self, last_credentials=credentials)


@dataclass(frozen=True, slots=True)
class ResolvedAuthProfile:
    profile_id: str
    name: str
    url: str | None
    access_token: str | None
    cookies: dict[str, str] = field(default_factory=dict)
    token_key: str | None = None
    expiry: datetime | None = None
