from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,95}$")
_MAX_MODELS = 5_000
_MAX_TAGS = 32


@dataclass(frozen=True)
class ModelRecord:
    name: str
    version: str
    source: str
    feature_count: int
    artifact_digest: str | None
    tags: tuple[str, ...]
    registered_at: str
    deployment_verified: bool = False

    def key(self) -> str:
        return f"{self.name}:{self.version}"


class ModelRegistry:
    """Bounded in-memory metadata registry.

    This registry records model metadata only. It does not fetch, sign, scan, load, deploy,
    evaluate, or attest model artifacts.
    """

    def __init__(self) -> None:
        self._records: dict[str, ModelRecord] = {}

    def register(
        self,
        *,
        name: str,
        version: str,
        source: str,
        feature_count: int,
        artifact_digest: str | None = None,
        tags: tuple[str, ...] = (),
        registered_at: str | None = None,
    ) -> ModelRecord:
        name = _token(name, "name")
        version = _token(version, "version")
        source = _bounded(source, "source", 1, 256)
        if not isinstance(feature_count, int) or isinstance(feature_count, bool) or not 1 <= feature_count <= 100_000:
            raise ValueError("feature_count must be an integer between 1 and 100000")
        if len(tags) > _MAX_TAGS:
            raise ValueError("too many tags")
        normalized_tags = tuple(sorted({_token(tag, "tag") for tag in tags}))
        digest = _normalize_digest(artifact_digest)
        timestamp = _timestamp(registered_at)
        record = ModelRecord(
            name=name,
            version=version,
            source=source,
            feature_count=feature_count,
            artifact_digest=digest,
            tags=normalized_tags,
            registered_at=timestamp,
            deployment_verified=False,
        )
        key = record.key()
        if key in self._records:
            raise ValueError("model version already registered")
        if len(self._records) >= _MAX_MODELS:
            raise ValueError("registry capacity exceeded")
        self._records[key] = record
        return record

    def get(self, name: str, version: str) -> ModelRecord:
        key = f"{_token(name, 'name')}:{_token(version, 'version')}"
        try:
            return self._records[key]
        except KeyError as exc:
            raise KeyError("model version not found") from exc

    def list(self, *, name: str | None = None, tag: str | None = None) -> tuple[ModelRecord, ...]:
        name_filter = _token(name, "name") if name is not None else None
        tag_filter = _token(tag, "tag") if tag is not None else None
        records = [
            record
            for record in self._records.values()
            if (name_filter is None or record.name == name_filter)
            and (tag_filter is None or tag_filter in record.tags)
        ]
        return tuple(sorted(records, key=lambda record: (record.name, record.version)))


def record_from_serving_info(*, name: str, version: str, source: str, feature_count: int) -> ModelRecord:
    """Create an unpersisted registry-compatible record from the inference service contract."""
    if not isinstance(feature_count, int) or isinstance(feature_count, bool) or not 1 <= feature_count <= 100_000:
        raise ValueError("feature_count must be an integer between 1 and 100000")
    return ModelRecord(
        name=_token(name, "name"),
        version=_token(version, "version"),
        source=_bounded(source, "source", 1, 256),
        feature_count=feature_count,
        artifact_digest=None,
        tags=(),
        registered_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        deployment_verified=False,
    )


def _token(value: str, label: str) -> str:
    normalized = _bounded(value, label, 1, 96).lower()
    if not _ID_RE.fullmatch(normalized):
        raise ValueError(f"invalid {label}")
    return normalized


def _bounded(value: str, label: str, minimum: int, maximum: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    normalized = value.strip()
    if not minimum <= len(normalized) <= maximum:
        raise ValueError(f"invalid {label} length")
    return normalized


def _normalize_digest(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", normalized):
        raise ValueError("artifact_digest must be sha256:<64 hex chars>")
    return normalized


def _timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid registered_at") from exc
    if parsed.tzinfo is None:
        raise ValueError("registered_at must include timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
