"""
ParkingFloor Model
==================
Represents a single floor in the multi-level parking lot.
Each floor holds a collection of ParkingSlots partitioned by vehicle type.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from enums.vehicle_type import VehicleType
from models.parking_slot import ParkingSlot


class FloorStatus:
    """Constants for floor operational status."""
    OPEN   = "OPEN"
    CLOSED = "CLOSED"


class ParkingFloor:
    """
    Manages a single floor containing multiple ParkingSlots.

    Attributes:
        floor_number : Unique identifier (1-indexed).
        floor_status : Whether the floor is OPEN or CLOSED.
    """

    def __init__(self, floor_number: int) -> None:
        if floor_number <= 0:
            raise ValueError("Floor number must be a positive integer.")
        self._floor_number: int = floor_number
        self._floor_status: str = FloorStatus.OPEN
        # Slots stored in a flat list; each slot carries its own type.
        self._slots: List[ParkingSlot] = []

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def floor_number(self) -> int:
        return self._floor_number

    @property
    def floor_status(self) -> str:
        return self._floor_status

    @property
    def slots(self) -> List[ParkingSlot]:
        return list(self._slots)  # return a copy

    # ------------------------------------------------------------------ #
    # Slot Management
    # ------------------------------------------------------------------ #

    def add_slot(self, slot: ParkingSlot) -> None:
        """Add a new ParkingSlot to this floor."""
        # Prevent duplicate slot numbers
        if any(s.slot_number == slot.slot_number for s in self._slots):
            raise ValueError(
                f"Slot {slot.slot_number} already exists on floor {self._floor_number}."
            )
        self._slots.append(slot)

    def add_slots(self, slots: List[ParkingSlot]) -> None:
        """Bulk-add multiple slots to this floor."""
        for slot in slots:
            self.add_slot(slot)

    def get_available_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        """Return the first available slot that matches the vehicle type."""
        for slot in self._slots:
            if slot.slot_type == vehicle_type and slot.is_available():
                return slot
        return None

    def get_slot_by_number(self, slot_number: int) -> Optional[ParkingSlot]:
        """Return slot object by its number, or None if not found."""
        for slot in self._slots:
            if slot.slot_number == slot_number:
                return slot
        return None

    # ------------------------------------------------------------------ #
    # Querying
    # ------------------------------------------------------------------ #

    def available_slots(self, vehicle_type: Optional[VehicleType] = None) -> List[ParkingSlot]:
        """
        Return list of available slots.
        Optionally filter by vehicle type.
        """
        return [
            s for s in self._slots
            if s.is_available() and (vehicle_type is None or s.slot_type == vehicle_type)
        ]

    def view_slots(self, vehicle_type: Optional[VehicleType] = None) -> None:
        """Print all slots on this floor, optionally filtered by type."""
        header = f"\n  Floor {self._floor_number} | Status: {self._floor_status}"
        if vehicle_type:
            header += f" | Filter: {vehicle_type.value}"
        print(header)
        print("  " + "-" * 60)

        slots_to_show = (
            [s for s in self._slots if s.slot_type == vehicle_type]
            if vehicle_type
            else self._slots
        )

        if not slots_to_show:
            print("  No slots found.")
            return

        for slot in slots_to_show:
            print(slot)

    def books_slot(self, slot: ParkingSlot, vehicle) -> None:
        """Book a specific slot for a vehicle (delegates to ParkingSlot)."""
        slot.book_slot(vehicle)

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #

    def get_occupancy_summary(self) -> Dict[str, int]:
        """Return total, occupied, and available counts per vehicle type."""
        summary: Dict[str, dict] = {}
        for vtype in VehicleType:
            all_of_type = [s for s in self._slots if s.slot_type == vtype]
            occupied    = [s for s in all_of_type if not s.is_available()]
            summary[vtype.value] = {
                "total":     len(all_of_type),
                "occupied":  len(occupied),
                "available": len(all_of_type) - len(occupied),
            }
        return summary

    def __str__(self) -> str:
        total     = len(self._slots)
        available = sum(1 for s in self._slots if s.is_available())
        return (
            f"Floor {self._floor_number} | Status: {self._floor_status} "
            f"| Slots: {total} total, {available} available"
        )

    def __repr__(self) -> str:
        return f"ParkingFloor(floor_number={self._floor_number}, status={self._floor_status})"
