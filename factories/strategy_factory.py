"""
Strategy Factory
================
Design Pattern: Factory Method
  - Centralises creation of Strategy objects.
  - Client code never hard-codes which strategy to use; it asks the factory.
  - New strategies can be registered without touching existing code.
"""

from strategies.fee_strategy import FeeStrategy, HourlyFeeStrategy, FlatFeeStrategy
from strategies.slot_allocation import SlotAllocationStrategy, FirstAvailableStrategy
from typing import Dict, Type


class StrategyFactory:
    """
    Factory for creating Fee and Slot-Allocation strategy instances.

    Usage:
        fee_strategy  = StrategyFactory.get_fee_strategy("hourly")
        slot_strategy = StrategyFactory.get_slot_strategy("first_available")
    """

    # ------------------------------------------------------------------
    # Fee strategies registry
    # ------------------------------------------------------------------

    _FEE_REGISTRY: Dict[str, Type[FeeStrategy]] = {
        "hourly":        HourlyFeeStrategy,
        "flat":          FlatFeeStrategy,
    }

    @classmethod
    def get_fee_strategy(cls, name: str = "hourly") -> FeeStrategy:
        """
        Return an instance of the requested fee strategy.

        Args:
            name: Key from _FEE_REGISTRY (case-insensitive). Defaults to "hourly".

        Raises:
            ValueError: if the strategy name is not registered.
        """
        strategy_class = cls._FEE_REGISTRY.get(name.lower())
        if strategy_class is None:
            raise ValueError(
                f"Unknown fee strategy: '{name}'. "
                f"Registered strategies: {list(cls._FEE_REGISTRY.keys())}"
            )
        return strategy_class()

    @classmethod
    def register_fee_strategy(cls, name: str, strategy_class: Type[FeeStrategy]) -> None:
        """Extensibility hook: register a new fee strategy at runtime."""
        cls._FEE_REGISTRY[name.lower()] = strategy_class

    # ------------------------------------------------------------------
    # Slot allocation strategies registry
    # ------------------------------------------------------------------

    _SLOT_REGISTRY: Dict[str, Type[SlotAllocationStrategy]] = {
        "first_available": FirstAvailableStrategy,
    }

    @classmethod
    def get_slot_strategy(cls, name: str = "first_available") -> SlotAllocationStrategy:
        """
        Return an instance of the requested slot allocation strategy.

        Args:
            name: Key from _SLOT_REGISTRY. Defaults to "first_available".

        Raises:
            ValueError: if the strategy name is not registered.
        """
        strategy_class = cls._SLOT_REGISTRY.get(name.lower())
        if strategy_class is None:
            raise ValueError(
                f"Unknown slot strategy: '{name}'. "
                f"Registered strategies: {list(cls._SLOT_REGISTRY.keys())}"
            )
        return strategy_class()

    @classmethod
    def register_slot_strategy(cls, name: str, strategy_class: Type[SlotAllocationStrategy]) -> None:
        """Extensibility hook: register a new slot allocation strategy at runtime."""
        cls._SLOT_REGISTRY[name.lower()] = strategy_class
