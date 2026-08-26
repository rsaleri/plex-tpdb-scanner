"""Pydantic models for the Plex provider HTTP boundary."""

from typing import Any
from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict, Field, computed_field

from provider.config import get_settings
settings = get_settings()

class PlexMatchRequest(BaseModel):
    """Subset of Plex's match request used by this provider."""

    model_config = ConfigDict(extra="ignore")

    type: int = 1
    title: str = ""
    year: int | None = None
    filename: str = ""

    @computed_field
    @property
    def effective_title(self) -> str:
        if not self.filename or settings.tpdb_prefer_filename == 0:
            return self.title
        return PurePosixPath(self.filename).stem

class PlexImage(BaseModel):
    """Canonical Plex image asset."""

    model_config = ConfigDict(extra="allow")

    type: str
    url: str
    key: str | None = None
    ratingKey: str | None = None
    provider: str | None = None


class PlexMetadata(BaseModel):
    """Flexible Plex metadata item with validated image assets."""

    model_config = ConfigDict(extra="allow")

    type: str | None = None
    ratingKey: str | None = None
    Image: list[PlexImage] | None = None


class PlexMediaContainer(BaseModel):
    """Flexible Plex response envelope with validated image assets."""

    model_config = ConfigDict(extra="allow")

    identifier: str
    offset: int = 0
    totalSize: int = 0
    size: int = 0
    Metadata: list[PlexMetadata] | None = None
    Image: list[PlexImage] | None = None


class PlexResponse(BaseModel):
    """Top-level Plex response object."""

    MediaContainer: PlexMediaContainer


def plex_response(container: PlexMediaContainer) -> dict[str, Any]:
    """Serialize a validated Plex response for FastAPI."""
    return PlexResponse(MediaContainer=container).model_dump(
        mode="json",
        exclude_none=True,
        by_alias=True,
    )
