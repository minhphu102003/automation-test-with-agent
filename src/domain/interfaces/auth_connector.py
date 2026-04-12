from abc import ABC, abstractmethod

from src.domain.entities.auth_profile import AuthCredentials, AuthProfile


class IAuthConnector(ABC):
    @abstractmethod
    async def fetch_credentials(self, profile: AuthProfile) -> AuthCredentials:
        """Fetch fresh credentials for the supplied auth profile."""
        raise NotImplementedError
