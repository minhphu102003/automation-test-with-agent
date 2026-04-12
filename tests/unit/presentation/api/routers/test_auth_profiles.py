# ruff: noqa: E402

import sys
import types
from pathlib import Path
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

fake_redis = types.ModuleType("redis")
fake_redis_asyncio = types.ModuleType("redis.asyncio")


class _FakeRedisClient:
    @classmethod
    def from_url(cls, *args, **kwargs):
        return cls()

    async def close(self):
        return None


fake_redis_asyncio.Redis = _FakeRedisClient
fake_redis_asyncio.from_url = _FakeRedisClient.from_url
fake_redis.asyncio = fake_redis_asyncio
sys.modules.setdefault("redis", fake_redis)
sys.modules.setdefault("redis.asyncio", fake_redis_asyncio)

fake_aioboto3 = types.ModuleType("aioboto3")
fake_aioboto3.Session = lambda *args, **kwargs: object()
sys.modules.setdefault("aioboto3", fake_aioboto3)

fake_browser_use = types.ModuleType("browser_use")


class _Placeholder:
    def __init__(self, *args, **kwargs):
        pass


class _FakeTools:
    def action(self, description):
        def decorator(func):
            return func

        return decorator


class _FakeActionResult:
    def __init__(self, extracted_content=None):
        self.extracted_content = extracted_content


fake_browser_use.Agent = _Placeholder
fake_browser_use.BrowserSession = _Placeholder
fake_browser_use.BrowserProfile = _Placeholder
fake_browser_use.ChatOpenAI = _Placeholder
fake_browser_use.ChatGoogle = _Placeholder
fake_browser_use.AgentHistoryList = object
fake_browser_use.Tools = _FakeTools
fake_browser_use.ActionResult = _FakeActionResult
sys.modules.setdefault("browser_use", fake_browser_use)

fake_langfuse = types.ModuleType("langfuse")
fake_langfuse.Langfuse = _Placeholder
sys.modules.setdefault("langfuse", fake_langfuse)

fake_langchain_openai = types.ModuleType("langchain_openai")
fake_langchain_openai.ChatOpenAI = _Placeholder
sys.modules.setdefault("langchain_openai", fake_langchain_openai)

from src.application.use_cases.manage_profiles import ManageProfilesUseCase
from src.domain.exceptions.base import AppBaseException
from src.infrastructure.di import providers
from src.infrastructure.external.auth_connector import HttpAuthConnector
from src.infrastructure.storage.json_profile_repository import JsonAuthProfileRepository
from src.presentation.api.error_handlers import global_exception_handler
from src.presentation.api.routers import auth_profiles


class AuthProfilesRouterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        repository = JsonAuthProfileRepository(str(Path(self.temp_dir.name) / "profiles.json"))
        connector = HttpAuthConnector()
        self.use_case = ManageProfilesUseCase(repository, connector)

        app = FastAPI()
        app.add_exception_handler(Exception, global_exception_handler)
        app.add_exception_handler(AppBaseException, global_exception_handler)
        app.include_router(auth_profiles.router, prefix="/api/v1")
        app.dependency_overrides[providers.get_manage_profiles_use_case] = lambda: self.use_case
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_crud_endpoints_manage_profiles(self) -> None:
        create_response = self.client.post(
            "/api/v1/auth-profiles/",
            json={
                "profile_id": "staging",
                "name": "Staging",
                "auth_config": {
                    "url": "https://auth.example.com/token",
                    "method": "POST",
                    "body": {"username": "qa"},
                    "header": {"X-App": "browser-testing"},
                    "mapping_path": {"token": "data.token", "expiry": "data.expiry"},
                    "token_key": "access_token",
                },
            },
        )
        self.assertEqual(201, create_response.status_code)
        self.assertEqual("staging", create_response.json()["profile_id"])

        list_response = self.client.get("/api/v1/auth-profiles/")
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(1, len(list_response.json()))

        update_response = self.client.put(
            "/api/v1/auth-profiles/staging",
            json={
                "name": "Staging Updated",
                "auth_config": {
                    "url": "https://auth.example.com/refresh",
                    "method": "POST",
                    "body": {},
                    "header": {},
                    "mapping_path": "token",
                },
            },
        )
        self.assertEqual(200, update_response.status_code)
        self.assertEqual("Staging Updated", update_response.json()["name"])

        delete_response = self.client.delete("/api/v1/auth-profiles/staging")
        self.assertEqual(204, delete_response.status_code)

        missing_response = self.client.get("/api/v1/auth-profiles/staging")
        self.assertEqual(404, missing_response.status_code)
