"""
Factories Package
=================
Contains Factory pattern implementations for:
  - VehicleFactory  : creates Vehicle subclass instances
  - StrategyFactory : creates Strategy instances
"""

from .vehicle_factory import VehicleFactory
from .strategy_factory import StrategyFactory

__all__ = ["VehicleFactory", "StrategyFactory"]
