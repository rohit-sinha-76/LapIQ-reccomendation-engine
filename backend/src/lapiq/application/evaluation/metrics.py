"""Evaluation metrics dataclasses for offline persona testing."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AccuracyMetrics:
    """Calculated Top-1 and Top-3 accuracy metrics across all evaluated personas."""

    total_personas: int
    top1_correct_count: int
    top3_correct_count: int
    top1_accuracy_percent: float
    top3_accuracy_percent: float
    persona_results: list[dict[str, str | bool | float]] = field(default_factory=list)
