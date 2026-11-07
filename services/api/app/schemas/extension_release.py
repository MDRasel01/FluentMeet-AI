from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ExtensionReleaseBase(BaseModel):
    version: str = Field(..., description="Semantic version string (e.g. 1.0.0)")
    channel: str = Field("stable", description="Release channel: stable, beta, or internal")
    minimum_chrome_version: str = Field("116.0", description="Minimum supported Chrome browser version")
    release_notes: Optional[Union[List[str], Dict[str, Any], str]] = Field(None, description="Release notes or changelog")
    git_commit_sha: Optional[str] = Field(None, description="Git commit reference")
    build_number: Optional[str] = Field(None, description="Build identifier")

class ExtensionReleaseCreate(ExtensionReleaseBase):
    extension_name: Optional[str] = Field("FluentMeet AI — Real-time English Meeting Coach")

class ExtensionReleaseUpdate(BaseModel):
    minimum_chrome_version: Optional[str] = None
    release_notes: Optional[Union[List[str], Dict[str, Any], str]] = None

class ExtensionReleaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    extension_name: str
    version: str
    channel: str
    status: str
    manifest_version: int
    build_number: Optional[str] = None
    git_commit_sha: Optional[str] = None
    release_notes: Optional[Any] = None
    minimum_chrome_version: str
    artifact_filename: Optional[str] = None
    artifact_size_bytes: int
    sha256_checksum: Optional[str] = None
    download_count: int
    download_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ExtensionReleaseListResponse(BaseModel):
    items: List[ExtensionReleaseResponse]
    total: int
    current_stable: Optional[ExtensionReleaseResponse] = None

class ExtensionDownloadLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    release_id: str
    user_id: Optional[str] = None
    downloaded_at: datetime
    download_status: str
    client_platform: str

class ExtensionAnalyticsResponse(BaseModel):
    total_releases: int
    published_releases: int
    total_downloads: int
    current_stable_version: Optional[str] = None
    downloads_by_platform: Dict[str, int]
    downloads_by_version: Dict[str, int]
    recent_downloads: List[Dict[str, Any]]
