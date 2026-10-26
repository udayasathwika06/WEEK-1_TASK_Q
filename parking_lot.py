"""
ParkingLot — Singleton
======================
Design Pattern: Singleton
  - Ensures exactly one ParkingLot instance exists throughout the application.
  - Provides a global access point for floor management.
  - Matches UML: ParkingLot has name, floors_available (List<int>),
    view_floors(), get_floor(vehicle), exit_lot().
"""

from __future__ import annotations

from typing import Dict, List, Optional

from models.parking_floor import ParkingFloor
from models.parking_slot import ParkingSlot
from enums.vehicle_type import VehicleType


class ParkingLot:
    """
    Singleton representing the entire parking facility.

    Only one instance exists per application run. Use ParkingLot.get_instance()
    to access it rather than calling the constructor directly.
    """

    _instance: Optional["ParkingLot"] = None

    def __new__(cls, name: str = "City Parking Lot") -> "ParkingLot":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, name: str = "City Parking Lot") -> None:
        # Prevent re-initialisation on repeated calls
        if self._initialized:
            return
        self._name: str = name
        self._floors: Dict[int, ParkingFloor] = {}   # floor_number -> ParkingFloor
        self._initialized: bool = True

    # ------------------------------------------------------------------ #
    # Singleton accessor
    # ------------------------------------------------------------------ #

    @classmethod
    def get_instance(cls, name: str = "City Parking Lot") -> "ParkingLot":
        """Return the single ParkingLot instance, creating it if necessary."""
        return cls(name)

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton (used in unit tests to get a clean state).
        NOT intended for production use.
        """
        cls._instance = None

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        return self._name

    @property
    def floors_available(self) -> List[int]:
        """Returns sorted list of floor numbers currently in the lot."""
        return sorted(self._floors.keys())

    # ------------------------------------------------------------------ #
    # Floor Management
    # ------------------------------------------------------------------ #

    def add_floor(self, floor: ParkingFloor) -> None:
        """
        Add a ParkingFloor to the lot.

        Raises:
            ValueError: if a floor with the same number already exists.
        """
        if floor.floor_number in self._floors:
            raise ValueError(
                f"Floor {floor.floor_number} already exists in the parking lot."
            )
        self._floors[floor.floor_number] = floor
        print(f"[INFO] Floor {floor.floor_number} added to '{self._name}'.")

    def get_floor(self, floor_number: int) -> Optional[ParkingFloor]:
        """
        Retrieve a floor by its number.

        Returns:
            ParkingFloor if found, else None.
        """
        return self._floors.get(floor_number)

    def get_all_floors(self) -> List[ParkingFloor]:
        """Return list of floors sorted by floor number."""
        return [self._floors[k] for k in sorted(self._floors)]

    # ------------------------------------------------------------------ #
    # Display
    # ------------------------------------------------------------------ #

    def view_floors(self) -> None:
        """Print a summary of all floors and their occupancy."""
        print(f"\n{'=' * 60}")
        print(f"  PARKING LOT: {self._name}")
        print(f"  Total Floors: {len(self._floors)}")
        print(f"{'=' * 60}")
        if not self._floors:
            print("  No floors added yet.")
            return
        for floor in self.get_all_floors():
            print(f"  {floor}")
        print(f"{'=' * 60}\n")

    def view_free_slots_by_type(self, vehicle_type: VehicleType) -> None:
        """Display all available slots for a given vehicle type across all floors."""
        print(f"\n  Available slots for {vehicle_type.value}:")
        print("  " + "-" * 50)
        found_any = False
        for floor in self.get_all_floors():
            free = floor.available_slots(vehicle_type)
            if free:
                found_any = True
                print(f"\n  Floor {floor.floor_number}:")
                for slot in free:
                    print(f"    Slot {slot.slot_number}")
        if not found_any:
            print(f"  No available slots for {vehicle_type.value}.")

    def display_occupancy(self) -> None:
        """Print detailed occupancy table across all floors."""
        print(f"\n{'=' * 70}")
        print(f"  OCCUPANCY REPORT — {self._name}")
        print(f"{'=' * 70}")
        print(f"  {'Floor':<8} {'Type':<8} {'Total':<8} {'Occupied':<10} {'Available':<10}")
        print("  " + "-" * 50)
        for floor in self.get_all_floors():
            summary = floor.get_occupancy_summary()
            for vtype, counts in summary.items():
                if counts["total"] > 0:
                    print(
                        f"  {floor.floor_number:<8} {vtype:<8} "
                        f"{counts['total']:<8} {counts['occupied']:<10} "
                        f"{counts['available']:<10}"
                    )
        print(f"{'=' * 70}\n")

    def exit_lot(self) -> None:
        """Simulate closing the lot (display summary and teardown message)."""
        print(f"\n[INFO] Closing '{self._name}'...")
        self.display_occupancy()
        print(f"[INFO] '{self._name}' is now CLOSED. Thank you!\n")

    # ------------------------------------------------------------------ #
    # Dunder
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        return f"ParkingLot(name='{self._name}', floors={self.floors_available})"

    def __repr__(self) -> str:
        return self.__str__()
