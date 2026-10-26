"""
Fee Strategy
============
Design Pattern: Strategy
  - FeeStrategy is the abstract interface for pricing algorithms.
  - HourlyFeeStrategy charges based on duration (tiered per vehicle type).
  - FlatFeeStrategy charges a fixed fee regardless of duration.
  - Adding a new pricing model (e.g., DailyFeeStrategy) requires ONLY adding
    a new class; no existing code changes needed.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

from enums.vehicle_type import VehicleType


class FeeStrategy(ABC):
    """Abstract base class for all fee calculation strategies."""

    @abstractmethod
    def calculate_fee(
        self,
        entry_time: datetime,
        exit_time: datetime,
        vehicle_type: VehicleType
    ) -> float:
        """
        Calculate parking fee for a vehicle.

        Args:
            entry_time: When the vehicle entered the lot.
            exit_time:  When the vehicle is exiting the lot.
            vehicle_type: The type of vehicle being charged.

        Returns:
            Total fee as a float.
        """
        pass

    def _hours_parked(self, entry_time: datetime, exit_time: datetime) -> float:
        """Utility: returns hours parked (minimum 1 hour)."""
        delta = exit_time - entry_time
        hours = delta.total_seconds() / 3600
        return max(hours, 1.0)  # minimum 1-hour charge


# ---------------------------------------------------------------------------
# Concrete Strategy 1: Hourly Fee
# ---------------------------------------------------------------------------

class HourlyFeeStrategy(FeeStrategy):
    """
    Charges by the hour based on vehicle type.

    Rates (per hour):
      BIKE  -> ₹10
      CAR   -> ₹20
      TRUCK -> ₹50

    Adding a new vehicle type only requires updating the RATES dict.
    """

    RATES: Dict[VehicleType, float] = {
        VehicleType.BIKE:  10.0,
        VehicleType.CAR:   20.0,
        VehicleType.TRUCK: 50.0,
    }

    def calculate_fee(
        self,
        entry_time: datetime,
        exit_time: datetime,
        vehicle_type: VehicleType
    ) -> float:
        hours = self._hours_parked(entry_time, exit_time)
        rate = self.RATES.get(vehicle_type, 0.0)
        fee = hours * rate
        return round(fee, 2)

    def __str__(self) -> str:
        return "HourlyFeeStrategy"


# ---------------------------------------------------------------------------
# Concrete Strategy 2: Flat Fee
# ---------------------------------------------------------------------------

class FlatFeeStrategy(FeeStrategy):
    """
    Charges a flat fixed fee per vehicle type, regardless of duration.

    Flat Fees:
      BIKE  -> ₹30
      CAR   -> ₹80
      TRUCK -> ₹150

    Adding a new vehicle type only requires updating the FLAT_FEES dict.
    """

    FLAT_FEES: Dict[VehicleType, float] = {
        VehicleType.BIKE:  30.0,
        VehicleType.CAR:   80.0,
        VehicleType.TRUCK: 150.0,
    }

    def calculate_fee(
        self,
        entry_time: datetime,
        exit_time: datetime,
        vehicle_type: VehicleType
    ) -> float:
        return self.FLAT_FEES.get(vehicle_type, 0.0)

    def __str__(self) -> str:
        return "FlatFeeStrategy"
