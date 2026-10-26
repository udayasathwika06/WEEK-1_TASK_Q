"""
ParkingSlot Model
=================
Represents a single physical parking space on a floor.
Each slot has a type (vehicle it can accommodate), a number, and a status.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from enums.vehicle_type import VehicleType

if TYPE_CHECKING:
    from models.vehicle import Vehicle


class SlotStatus:
    """Simple string constants for slot status (avoids magic strings)."""
    AVAILABLE = "AVAILABLE"
    OCCUPIED  = "OCCUPIED"


class ParkingSlot:
    """
    Represents one parking slot.

    Attributes:
        slot_number  : Unique identifier within a floor.
        slot_type    : The VehicleType this slot is designated for.
        slot_status  : Current status ("AVAILABLE" or "OCCUPIED").
    """

    def __init__(self, slot_number: int, slot_type: VehicleType) -> None:
        self._slot_number: int = slot_number
        self._slot_type: VehicleType = slot_type
        self._slot_status: str = SlotStatus.AVAILABLE
        self._vehicle: Optional["Vehicle"] = None

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def slot_number(self) -> int:
        return self._slot_number

    @property
    def slot_type(self) -> VehicleType:
        return self._slot_type

    @property
    def slot_status(self) -> str:
        return self._slot_status

    # ------------------------------------------------------------------ #
    # Public Methods
    # ------------------------------------------------------------------ #

    def is_available(self) -> bool:
        """Returns True if the slot is currently free."""
        return self._slot_status == SlotStatus.AVAILABLE

    def book_slot(
        self,
        vehicle: "Vehicle"
    ) -> None:
        """
        Mark this slot as occupied by the given vehicle.

        Raises:
            ValueError: if slot is already occupied.
        """
        if not self.is_available():
            raise ValueError(
                f"Slot {self._slot_number} is already OCCUPIED. Cannot book again."
            )
        self._vehicle = vehicle
        self._slot_status = SlotStatus.OCCUPIED

    def vacate_slot(self) -> None:
        """
        Mark this slot as available again (remove vehicle reference).

        Raises:
            ValueError: if slot is already available.
        """
        if self.is_available():
            raise ValueError(
                f"Slot {self._slot_number} is already AVAILABLE. Cannot vacate."
            )
        self._vehicle = None
        self._slot_status = SlotStatus.AVAILABLE

    def get_vehicle(self) -> Optional["Vehicle"]:
        """Returns the vehicle currently parked here, or None."""
        return self._vehicle

    # ------------------------------------------------------------------ #
    # Display
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        vehicle_info = (
            f" | Vehicle: {self._vehicle.number}" if self._vehicle else ""
        )
        return (
            f"  Slot {self._slot_number:>3} | Type: {self._slot_type.value:<5} "
            f"| Status: {self._slot_status:<9}{vehicle_info}"
        )

    def __repr__(self) -> str:
        return (
            f"ParkingSlot(slot_number={self._slot_number}, "
            f"slot_type={self._slot_type}, status={self._slot_status})"
        )
