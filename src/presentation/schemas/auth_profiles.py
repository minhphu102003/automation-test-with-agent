from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.domain.entities.auth_profile import AuthProfile


class AuthConfigPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str
    method: str = "POST"
    body: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("headers", "header"),
    )
    mapping_path: str | dict[str, str] | None = None
    expiry_mapping_path: str | None = None
    token_key: str | None = None
    auth_type: str = Field(default="api", validation_alias=AliasChoices("auth_type", "mode"))
    metadata: dict[str, Any] = Field(default_factory=dict)


class LastCredentialsPayload(BaseModel):
    token: str | None = None
    cookies: dict[str, str] = Field(default_factory=dict)
    expiry: datetime | None = None


class AuthProfileCreateRequest(BaseModel):
    profile_id: str | None = None
    name: str
    auth_config: AuthConfigPayload
    last_credentials: LastCredentialsPayload | None = None


class AuthProfileUpdateRequest(BaseModel):
    name: str | None = None
    auth_config: AuthConfigPayload | None = None
    last_credentials: LastCredentialsPayload | None = None


class AuthProfileResponse(BaseModel):
    profile_id: str
    name: str
    auth_config: AuthConfigPayload
    last_credentials: LastCredentialsPayload

    @classmethod
    def from_domain(cls, profile: AuthProfile) -> "AuthProfileResponse":
        return cls.model_validate(profile.to_dict())
