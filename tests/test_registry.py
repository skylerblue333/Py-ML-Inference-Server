from src.model import ModelInfo
from src.registry import ModelRegistry, record_from_serving_info


def test_registry_is_deterministic_and_versioned() -> None:
    registry = ModelRegistry()
    first = registry.register(
        name="demo-linear",
        version="v1",
        source="built-in-demo",
        feature_count=3,
        artifact_digest="sha256:" + "a" * 64,
        tags=("demo", "linear", "demo"),
        registered_at="2026-08-25T00:00:00Z",
    )
    second = registry.register(
        name="demo-linear",
        version="v2",
        source="environment",
        feature_count=3,
        tags=("linear",),
        registered_at="2026-08-25T01:00:00+00:00",
    )

    assert first.tags == ("demo", "linear")
    assert first.deployment_verified is False
    assert registry.get("DEMO-LINEAR", "V1") == first
    assert registry.list(name="demo-linear") == (first, second)
    assert registry.list(tag="demo") == (first,)


def test_registry_rejects_duplicates_and_bad_digest() -> None:
    registry = ModelRegistry()
    registry.register(name="m", version="v1", source="caller", feature_count=1)
    try:
        registry.register(name="m", version="v1", source="caller", feature_count=1)
        raise AssertionError("expected duplicate failure")
    except ValueError as exc:
        assert "already registered" in str(exc)

    try:
        ModelRegistry().register(name="m", version="v1", source="caller", feature_count=1, artifact_digest="abc")
        raise AssertionError("expected digest failure")
    except ValueError as exc:
        assert "sha256" in str(exc)


def test_serving_model_info_maps_to_registry_contract() -> None:
    info = ModelInfo(name="demo-linear", version="demo-v1", source="built-in-demo", feature_count=3)
    record = record_from_serving_info(
        name=info.name,
        version=info.version,
        source=info.source,
        feature_count=info.feature_count,
    )
    assert record.name == info.name
    assert record.version == info.version
    assert record.feature_count == info.feature_count
    assert record.deployment_verified is False


def test_serving_model_info_rejects_boolean_feature_count() -> None:
    try:
        record_from_serving_info(
            name="demo-linear",
            version="demo-v1",
            source="built-in-demo",
            feature_count=True,
        )
        raise AssertionError("expected boolean feature_count rejection")
    except ValueError as exc:
        assert "feature_count" in str(exc)
