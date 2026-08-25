# SkyModelRegistry — Wave 2 Slot #100

**Status:** engineering beta / model metadata registry.

SkyModelRegistry records bounded, versioned metadata for models used by SKYCOIN4444 components. It supports deterministic lookup/listing, tags, optional SHA-256 artifact digests, timestamps, and a compatibility contract with the existing inference service's `ModelInfo` metadata.

## Integration contract

The existing inference boundary can map its `ModelInfo(name, version, source, feature_count)` into a registry-compatible record through `record_from_serving_info`. This records metadata only and deliberately keeps `deployment_verified=False`.

## Security and truth boundary

The registry does not download artifacts, validate artifact contents, verify signatures, run malware scanning, evaluate models, measure accuracy, deploy models, authorize model use, prove provenance, or claim that any registered model is live. Persistence is process-local unless a consuming service adds a durable store.

An artifact digest is only caller-supplied metadata. A future artifact service must independently compute and compare digests before treating them as integrity evidence.
