from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.auth_profile import AuthProfile


class IAuthProfileRepository(ABC):
    @abstractmethod
    def list_profiles(self) -> list[AuthProfile]:
        raise NotImplementedError

    @abstractmethod
    def get_profile(self, profile_id: str) -> AuthProfile | None:
        raise NotImplementedError

    @abstractmethod
    def save_profile(self, profile: AuthProfile) -> AuthProfile:
        raise NotImplementedError

    @abstractmethod
    def delete_profile(self, profile_id: str) -> None:
        raise NotImplementedError
