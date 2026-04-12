from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.application.use_cases.manage_profiles import ManageAuthProfilesUseCase
from src.infrastructure.di import providers
from src.presentation.schemas.auth_profiles import (
    AuthProfileCreateRequest,
    AuthProfileResponse,
    AuthProfileUpdateRequest,
)


router = APIRouter(prefix="/auth-profiles", tags=["auth-profiles"])


@router.get("/", response_model=list[AuthProfileResponse])
async def list_auth_profiles(
    use_case: ManageAuthProfilesUseCase = Depends(providers.get_manage_auth_profiles_use_case),
):
    return [AuthProfileResponse.from_domain(profile) for profile in use_case.list_profiles()]


@router.post("/", response_model=AuthProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_auth_profile(
    request: AuthProfileCreateRequest,
    use_case: ManageAuthProfilesUseCase = Depends(providers.get_manage_auth_profiles_use_case),
):
    profile = use_case.create_profile(request.model_dump(by_alias=True))
    return AuthProfileResponse.from_domain(profile)


@router.get("/{profile_id}", response_model=AuthProfileResponse)
async def get_auth_profile(
    profile_id: str,
    use_case: ManageAuthProfilesUseCase = Depends(providers.get_manage_auth_profiles_use_case),
):
    return AuthProfileResponse.from_domain(use_case.get_profile(profile_id))


@router.put("/{profile_id}", response_model=AuthProfileResponse)
async def update_auth_profile(
    profile_id: str,
    request: AuthProfileUpdateRequest,
    use_case: ManageAuthProfilesUseCase = Depends(providers.get_manage_auth_profiles_use_case),
):
    profile = use_case.update_profile(profile_id, request.model_dump(exclude_none=True, by_alias=True))
    return AuthProfileResponse.from_domain(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_auth_profile(
    profile_id: str,
    use_case: ManageAuthProfilesUseCase = Depends(providers.get_manage_auth_profiles_use_case),
):
    use_case.delete_profile(profile_id)
