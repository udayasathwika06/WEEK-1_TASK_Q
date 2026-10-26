"""
Slot Allocation Strategy
========================
Design Pattern: Strategy
  - SlotAllocationStrategy is the abstract interface for slot-finding algorithms.
  - FirstAvailableStrategy scans floors in order and returns the first free slot.
  - Adding a new strategy (e.g., NearestEntranceStrategy) requires ONLY adding
    a new class; no existing code changes needed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Tuple

from enums.vehicle_type import VehicleType

if TYPE_CHECKING:
    from models.parking_floor import ParkingFloor
    from models.parking_slot import ParkingSlot


class SlotAllocationStrategy(ABC):
    """Abstract base class for slot allocation algorithms."""

    @abstractmethod
    def allocate(
        self,
        floors: List["ParkingFloor"],
        vehicle_type: VehicleType
    ) -> Optional[Tuple["ParkingFloor", "ParkingSlot"]]:
        """
        Find and return a (floor, slot) tuple suitable for the given vehicle type.

        Returns:
            A tuple of (ParkingFloor, ParkingSlot) if a slot is found, else None.
        """
        pass


# ---------------------------------------------------------------------------
# Concrete Strategy: First Available
# ---------------------------------------------------------------------------

class FirstAvailableStrategy(SlotAllocationStrategy):
    """
    Scans floors sequentially (floor 1, 2, 3…) and returns the first
    available slot matching the vehicle type.
    """

    def allocate(
        self,
        floors: List["ParkingFloor"],
        vehicle_type: VehicleType
    ) -> Optional[Tuple["ParkingFloor", "ParkingSlot"]]:
        for floor in floors:
            slot = floor.get_available_slot(vehicle_type)
            if slot:
                return floor, slot
        return None

    def __str__(self) -> str:
        return "FirstAvailableStrategy"
