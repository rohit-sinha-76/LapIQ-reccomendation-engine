"""Business Rules — availability, budget, and discontinued laptop filtering."""

from collections.abc import Sequence

from lapiq.domain.recommendation.models import UserPreferences
from lapiq.infrastructure.database.models import Variant

MAX_PRICE_BUFFER_PERCENT = 0.05  # Allow up to 5% over stated budget


class BusinessRulesFilter:
    """
    Applies deterministic business rules to candidate variants.

    Rules applied in order:
    1. Remove variants marked out of stock.
    2. Remove variants belonging to discontinued (unavailable) laptops.
    3. Remove variants exceeding budget with buffer.
    """

    def apply(self, candidates: Sequence[Variant], preferences: UserPreferences) -> list[Variant]:
        """Filter candidate list applying all three business rules."""
        max_price = int(preferences.budget_inr * (1 + MAX_PRICE_BUFFER_PERCENT))
        filtered: list[Variant] = []

        for variant in candidates:
            if not self._is_in_stock(variant):
                continue
            if not self._laptop_is_active(variant):
                continue
            if not self._within_budget(variant, max_price):
                continue
            filtered.append(variant)

        return filtered

    def _is_in_stock(self, variant: Variant) -> bool:
        """Rule 1: Variant must be in stock."""
        return variant.is_in_stock

    def _laptop_is_active(self, variant: Variant) -> bool:
        """Rule 2: Parent laptop must not be discontinued."""
        return variant.laptop.is_available if variant.laptop else False

    def _within_budget(self, variant: Variant, max_price: int) -> bool:
        """Rule 3: Variant price must fall within budget with allowed buffer."""
        return variant.current_price_inr <= max_price
