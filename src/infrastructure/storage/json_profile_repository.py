from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.domain.entities.auth_profile import AuthProfile
from src.domain.interfaces.auth_profile_repository import IAuthProfileRepository


class JsonAuthProfileRepository(IAuthProfileRepository):
    def __init__(self, file_path: str = "data/profiles.json") -> None:
        self.file_path = Path(file_path)

    def list_profiles(self) -> list[AuthProfile]:
        payload = self._read_payload()
        return [self._deserialize_profile(item) for item in payload["profiles"]]

    def get_profile(self, profile_id: str) -> AuthProfile | None:
        for profile in self.list_profiles():
            if profile.profile_id == profile_id:
                return profile
        return None

    def save_profile(self, profile: AuthProfile) -> AuthProfile:
        payload = self._read_payload()
        serialized_profile = self._serialize_profile(profile)

        for index, existing in enumerate(payload["profiles"]):
            if existing["profile_id"] == profile.profile_id:
                payload["profiles"][index] = serialized_profile
                self._write_payload(payload)
                return profile

        payload["profiles"].append(serialized_profile)
        self._write_payload(payload)
        return profile

    def delete_profile(self, profile_id: str) -> None:
        payload = self._read_payload()
        payload["profiles"] = [
            profile
            for profile in payload["profiles"]
            if profile["profile_id"] != profile_id
        ]
        self._write_payload(payload)

    def _read_payload(self) -> dict[str, list[dict[str, Any]]]:
        self._ensure_store()
        with self.file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            payload = {"profiles": payload}
        payload.setdefault("profiles", [])
        return payload

    def _write_payload(self, payload: dict[str, list[dict[str, Any]]]) -> None:
        self._ensure_store()
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _ensure_store(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text('{"profiles": []}', encoding="utf-8")

    def _serialize_profile(self, profile: AuthProfile) -> dict[str, Any]:
        return profile.to_dict()

    def _deserialize_profile(self, payload: dict[str, Any]) -> AuthProfile:
        return AuthProfile.from_dict(payload)
