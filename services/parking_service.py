"""
ParkingService — Controller / Service Layer
===========================================
Orchestrates all parking operations:
  - park_vehicle()   : validate, allocate slot, issue ticket
  - unpark_vehicle() : validate ticket, calculate fee, release slot
  - view_free_slots(): delegate to ParkingLot
  - display_occupancy(): delegate to ParkingLot

This layer keeps business logic separate from the domain models
and acts as the primary entry point for the driver / UI layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from parking_lot import ParkingLot
from models.ticket import Ticket
from enums.vehicle_type import VehicleType
from factories.vehicle_factory import VehicleFactory
from factories.strategy_factory import StrategyFactory
from strategies.fee_strategy import FeeStrategy
from strategies.slot_allocation import SlotAllocationStrategy


class ParkingServiceError(Exception):
    """Custom exception raised for business-rule violations in ParkingService."""
    pass


class ParkingService:
    """
    Service / Controller layer for the Parking Lot System.

    Responsibilities:
      - Input validation
      - Orchestration of Vehicle, ParkingFloor, ParkingSlot, and Ticket
      - Applying the correct FeeStrategy and SlotAllocationStrategy
      - Maintaining an active-ticket registry (ticket_id -> Ticket)
      - Maintaining a parked-vehicle registry (vehicle_number -> ticket_id)
        to prevent duplicate parking
    """

    def __init__(
        self,
        lot: Optional[ParkingLot] = None,
        fee_strategy: Optional[FeeStrategy] = None,
        slot_strategy: Optional[SlotAllocationStrategy] = None,
    ) -> None:
        self._lot: ParkingLot = lot or ParkingLot.get_instance()
        self._fee_strategy: FeeStrategy = (
            fee_strategy or StrategyFactory.get_fee_strategy("hourly")
        )
        self._slot_strategy: SlotAllocationStrategy = (
            slot_strategy or StrategyFactory.get_slot_strategy("first_available")
        )

        # Active tickets: ticket_id -> Ticket
        self._tickets: Dict[str, Ticket] = {}
        # Duplicate detection: vehicle_number -> ticket_id
        self._parked_vehicles: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Strategy setters (runtime swap — demonstrates Strategy pattern)
    # ------------------------------------------------------------------ #

    def set_fee_strategy(self, fee_strategy: FeeStrategy) -> None:
        self._fee_strategy = fee_strategy
        print(f"[INFO] Fee strategy switched to: {fee_strategy}")

    def set_slot_strategy(self, slot_strategy: SlotAllocationStrategy) -> None:
        self._slot_strategy = slot_strategy
        print(f"[INFO] Slot strategy switched to: {slot_strategy}")

    # ------------------------------------------------------------------ #
    # Park Vehicle
    # ------------------------------------------------------------------ #

    def park_vehicle(self, vehicle_type: VehicleType, vehicle_number: str) -> Ticket:
        """
        Park a vehicle in the lot and return a Ticket.

        Steps:
          1. Validate vehicle is not already parked.
          2. Use VehicleFactory to create the Vehicle object.
          3. Use SlotAllocationStrategy to find an available slot.
          4. Book the slot and create the Ticket.
          5. Register the ticket.

        Raises:
            ParkingServiceError: on duplicate vehicle, no slots available, etc.
        """
        # --- Validate duplicate ---
        if vehicle_number.upper() in self._parked_vehicles:
            existing_ticket_id = self._parked_vehicles[vehicle_number.upper()]
            raise ParkingServiceError(
                f"Vehicle '{vehicle_number}' is already parked. "
                f"Ticket: {existing_ticket_id}"
            )

        # --- Create vehicle via Factory (no if/else here) ---
        vehicle = VehicleFactory.create(vehicle_type, vehicle_number)

        # --- Allocate slot via Strategy (no if/else here) ---
        floors = self._lot.get_all_floors()
        result = self._slot_strategy.allocate(floors, vehicle_type)

        if result is None:
            raise ParkingServiceError(
                f"No available slots for {vehicle_type.value}. "
                "Parking lot is full for this vehicle type."
            )

        floor, slot = result

        # --- Book slot ---
        floor.books_slot(slot, vehicle)

        # --- Issue ticket ---
        ticket = Ticket(vehicle=vehicle, slot=slot, floor=floor)
        self._tickets[ticket.ticket_id] = ticket
        self._parked_vehicles[vehicle.number] = ticket.ticket_id

        print(f"\n[SUCCESS] Vehicle '{vehicle.number}' parked successfully.")
        print(ticket)
        return ticket

    # ------------------------------------------------------------------ #
    # Unpark Vehicle
    # ------------------------------------------------------------------ #

    def unpark_vehicle(self, ticket_id: str) -> float:
        """
        Process the exit of a parked vehicle using a ticket ID.

        Steps:
          1. Validate ticket exists.
          2. Validate ticket is still ACTIVE (prevent repeated exit).
          3. Calculate fee using FeeStrategy.
          4. Vacate the slot.
          5. Close the ticket.
          6. Remove from parked-vehicles registry.

        Args:
            ticket_id: The ticket ID string.

        Returns:
            Fee amount charged.

        Raises:
            ParkingServiceError: on invalid/closed ticket.
        """
        # --- Validate ticket exists ---
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise ParkingServiceError(
                f"Ticket '{ticket_id}' not found. Please provide a valid ticket."
            )

        # --- Validate ticket is active (no repeated exit) ---
        if not ticket.is_active():
            raise ParkingServiceError(
                f"Ticket '{ticket_id}' has already been processed. "
                "Repeated exit is not allowed."
            )

        # --- Calculate fee ---
        exit_time = datetime.now()
        fee = self._fee_strategy.calculate_fee(
            ticket.entry_time, exit_time, ticket.vehicle_type
        )

        # --- Vacate slot ---
        ticket.slot.vacate_slot()

        # --- Close ticket ---
        ticket.close(exit_time=exit_time, fee=fee)

        # --- Remove from active vehicle registry ---
        self._parked_vehicles.pop(ticket.vehicle.number, None)

        print(f"\n[SUCCESS] Vehicle '{ticket.vehicle.number}' has exited.")
        print(ticket)
        print(f"  Strategy Used : {self._fee_strategy}")
        return fee

    # ------------------------------------------------------------------ #
    # View Free Slots
    # ------------------------------------------------------------------ #

    def view_free_slots(self, vehicle_type: VehicleType) -> None:
        """Display available slots for the given vehicle type."""
        self._lot.view_free_slots_by_type(vehicle_type)

    # ------------------------------------------------------------------ #
    # Display Occupancy
    # ------------------------------------------------------------------ #

    def display_occupancy(self) -> None:
        """Display occupancy across all floors."""
        self._lot.display_occupancy()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Retrieve a ticket by ID (active or closed)."""
        return self._tickets.get(ticket_id)

    def is_vehicle_parked(self, vehicle_number: str) -> bool:
        """Check whether a vehicle is currently parked."""
        return vehicle_number.upper() in self._parked_vehicles

    def get_active_ticket_count(self) -> int:
        """Return number of currently active (open) tickets."""
        return sum(1 for t in self._tickets.values() if t.is_active())
