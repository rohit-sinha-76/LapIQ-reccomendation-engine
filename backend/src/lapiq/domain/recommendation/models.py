"""Domain data structures for the Recommendation Engine pipeline."""

from dataclasses import dataclass, field

from lapiq.infrastructure.database.models import Variant


@dataclass
class UserPreferences:
    """Structured user preferences extracted from conversation input."""

    budget_inr: int
    use_case: str
    target_segment: str
    min_ram_gb: int = 8
    min_storage_gb: int = 256
    preferred_brand: str | None = None
    requires_dedicated_gpu: bool = False
    prefers_lightweight: bool = False
    gaming_level: str | None = None


@dataclass(frozen=True)
class ScoredVariant:
    """Variant candidate with computed deterministic ranking scores."""

    variant: Variant
    total_score: float = 0.0
    performance_score: float = 0.0
    value_score: float = 0.0
    segment_fit_score: float = 0.0
    confidence_score: float = 0.0


@dataclass
class RecommendationResult:
    """Final recommendation output from the pipeline."""

    request_id: str
    preferences: UserPreferences
    ranked_variants: list[ScoredVariant] = field(default_factory=list)
    is_partial: bool = False
