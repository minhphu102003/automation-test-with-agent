from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.cookies import SimpleCookie
from typing import Any
from urllib import request as urllib_request

from src.domain.entities.auth_profile import AuthCredentials, AuthProfile
from src.domain.exceptions.base import DomainException
from src.domain.interfaces.auth_connector import IAuthConnector


class HttpAuthConnector(IAuthConnector):
    async def fetch_credentials(self, profile: AuthProfile) -> AuthCredentials:
        return await asyncio.to_thread(self._fetch_credentials_sync, profile)

    def _fetch_credentials_sync(self, profile: AuthProfile) -> AuthCredentials:
        auth_config = profile.auth_config
        headers = dict(auth_config.headers)
        method = auth_config.method.upper()
        data = None

        if auth_config.body:
            headers.setdefault("Content-Type", "application/json")
            data = json.dumps(auth_config.body).encode("utf-8")

        req = urllib_request.Request(
            auth_config.url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib_request.urlopen(req, timeout=30) as response:
                raw_body = response.read().decode("utf-8")
                payload = self._parse_response_body(raw_body)
                response_headers = response.headers
        except Exception as exc:
            raise DomainException(
                f"Failed to refresh auth profile '{profile.profile_id}': {exc}"
            ) from exc

        token = self._extract_token(payload, profile)
        cookies = self._extract_cookies(payload, response_headers, profile)
        expiry = self._extract_expiry(payload, response_headers, profile)

        if not token and not cookies:
            raise DomainException(
                f"Auth profile '{profile.profile_id}' did not return token or cookies"
            )

        return AuthCredentials(token=token, cookies=cookies, expiry=expiry)

    def _parse_response_body(self, raw_body: str) -> Any:
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return raw_body

    def _extract_token(self, payload: Any, profile: AuthProfile) -> str | None:
        mapping = profile.auth_config.mapping
        token_path = mapping.token_path
        if token_path:
            token = self._resolve_path(payload, token_path)
            return None if token is None else str(token)

        if isinstance(payload, dict):
            for key in ("token", "access_token", "accessToken"):
                if key in payload:
                    value = payload[key]
                    return None if value is None else str(value)

        return None

    def _extract_cookies(
        self,
        payload: Any,
        response_headers: Any,
        profile: AuthProfile,
    ) -> dict[str, str]:
        mapping = profile.auth_config.mapping
        resolved = self._resolve_path(payload, mapping.cookies_path) if mapping.cookies_path else None
        cookies = self._normalize_cookies(resolved)
        if cookies:
            return cookies

        header_values = []
        get_all = getattr(response_headers, "get_all", None)
        if callable(get_all):
            header_values = get_all("Set-Cookie") or []
        else:
            single_value = response_headers.get("Set-Cookie")
            if single_value:
                header_values = [single_value]

        normalized: dict[str, str] = {}
        for value in header_values:
            parsed = SimpleCookie()
            parsed.load(value)
            for cookie_name, morsel in parsed.items():
                normalized[cookie_name] = morsel.value
        return normalized

    def _extract_expiry(
        self,
        payload: Any,
        response_headers: Any,
        profile: AuthProfile,
    ) -> datetime | None:
        mapping = profile.auth_config.mapping
        raw_expiry = self._resolve_path(payload, mapping.expiry_path) if mapping.expiry_path else None
        expiry = self._normalize_expiry(raw_expiry)
        if expiry:
            return expiry

        raw_header = response_headers.get("X-Token-Expiry")
        if raw_header:
            return self._normalize_expiry(raw_header)
        return None

    def _normalize_cookies(self, value: Any) -> dict[str, str]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return {str(name): str(item) for name, item in value.items()}
        if isinstance(value, list):
            normalized: dict[str, str] = {}
            for item in value:
                if isinstance(item, dict) and "name" in item and "value" in item:
                    normalized[str(item["name"])] = str(item["value"])
            return normalized
        return {}

    def _normalize_expiry(self, value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, (int, float)):
            timestamp = float(value)
            if timestamp > 1_000_000_000_000:
                timestamp /= 1000
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                try:
                    parsed = parsedate_to_datetime(value)
                except (TypeError, ValueError):
                    return None
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        return None

    def _resolve_path(self, payload: Any, path: str | None) -> Any:
        if not path:
            return None

        current = payload
        for segment in path.split("."):
            if current is None:
                return None
            if isinstance(current, list):
                if not segment.isdigit():
                    return None
                index = int(segment)
                if index >= len(current):
                    return None
                current = current[index]
                continue
            if isinstance(current, dict):
                current = current.get(segment)
                continue
            return None
        return current


AuthConnector = HttpAuthConnector
