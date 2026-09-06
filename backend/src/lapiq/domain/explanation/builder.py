"""Explanation Builder — assembles structured prompt context from ranked results.

Business logic lives here. The LLM receives only structured data from this builder.
No ranking or filtering decisions are made inside prompt strings (invariant 6).
"""

from lapiq.domain.recommendation.models import RecommendationResult


class ExplanationContext:
    """Structured context package passed to ReasoningProvider for explanation generation."""

    def __init__(
        self,
        request_id: str,
        summary_text: str,
        evidence_items: list[dict[str, str]],
    ) -> None:
        self.request_id = request_id
        self.summary_text = summary_text
        self.evidence_items = evidence_items


class ExplanationBuilder:
    """
    Assembles deterministic structured context for the ReasoningProvider.

    Rules:
    - All recommendation logic is executed BEFORE this builder is called.
    - This builder only assembles and formats already-computed data.
    - No ranking, filtering, or scoring happens inside this class.
    - The prompt context is data-only; business rules are never embedded in it.
    """

    def build(
        self,
        result: RecommendationResult,
        evidence_by_laptop: dict[int, list[dict[str, str]]],
    ) -> ExplanationContext:
        """
        Build structured context from a completed RecommendationResult.

        Returns an ExplanationContext ready to stream to the ReasoningProvider.
        """
        lines: list[str] = []
        lines.append(f"User preference: {result.preferences.use_case}")
        lines.append(f"Segment: {result.preferences.target_segment}")
        lines.append(f"Budget: INR {result.preferences.budget_inr:,}")
        lines.append("")
        lines.append("Recommended laptops (already ranked by deterministic engine):")

        for rank, scored in enumerate(result.ranked_variants, start=1):
            v = scored.variant
            lines.append(
                f"{rank}. {v.laptop.brand} {v.laptop.model_name} — "
                f"INR {v.current_price_inr:,} | "
                f"RAM: {v.ram_gb}GB | Score: {scored.total_score:.2f} | "
                f"Confidence: {scored.confidence_score:.2f}"
            )
            laptop_id = v.laptop.id
            evidence = evidence_by_laptop.get(laptop_id, [])
            for ev in evidence[:2]:
                lines.append(f"   - [{ev['source_type']}] {ev['summary']}")

        lines.append("")
        lines.append(
            "Explain why these laptops suit the user's stated needs. "
            "Use factual, specific language."
        )

        summary_text = "\n".join(lines)

        all_evidence = []
        for items in evidence_by_laptop.values():
            all_evidence.extend(items)

        return ExplanationContext(
            request_id=result.request_id,
            summary_text=summary_text,
            evidence_items=all_evidence,
        )

    def build_fallback(self, result: RecommendationResult) -> ExplanationContext:
        """
        Build a deterministic markdown fallback explanation when Gemini is unavailable.

        This ensures core recommendation feature availability without LLM.
        """
        lines: list[str] = ["## LapIQ Recommendations\n"]
        lines.append(f"**Use case**: {result.preferences.use_case}")
        lines.append(f"**Segment**: {result.preferences.target_segment}")
        lines.append(f"**Budget**: INR {result.preferences.budget_inr:,}\n")

        for rank, scored in enumerate(result.ranked_variants, start=1):
            v = scored.variant
            lines.append(
                f"### {rank}. {v.laptop.brand} {v.laptop.model_name}\n"
                f"- **Price**: INR {v.current_price_inr:,}\n"
                f"- **RAM**: {v.ram_gb} GB\n"
                f"- **Storage**: {v.storage_gb} GB\n"
                f"- **Score**: {scored.total_score:.2f} | "
                f"**Confidence**: {scored.confidence_score:.2f}\n"
            )

        return ExplanationContext(
            request_id=result.request_id,
            summary_text="\n".join(lines),
            evidence_items=[],
        )
