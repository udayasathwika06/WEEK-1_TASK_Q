# -*- coding: utf-8 -*-
"""
Ticket Model
============
Generated when a vehicle successfully parks.
Carries all information needed to process the exit and calculate the fee.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from enums.vehicle_type import VehicleType

if TYPE_CHECKING:
    from models.parking_slot import ParkingSlot
    from models.parking_floor import ParkingFloor
    from models.vehicle import Vehicle


class TicketStatus:
    """Constants for ticket lifecycle status."""
    ACTIVE   = "ACTIVE"
    CLOSED   = "CLOSED"   # vehicle has exited


class Ticket:
    """
    Parking ticket issued on vehicle entry.

    Attributes:
        ticket_id    : Unique ticket identifier (UUID-based).
        vehicle_type : VehicleType of the parked vehicle.
        slot         : The ParkingSlot assigned.
        floor        : The ParkingFloor the slot belongs to.
        vehicle      : The Vehicle object.
        entry_time   : Timestamp of entry.
        status       : ACTIVE or CLOSED.
    """

    def __init__(
        self,
        vehicle: "Vehicle",
        slot: "ParkingSlot",
        floor: "ParkingFloor",
    ) -> None:
        self._ticket_id: str     = self._generate_ticket_id()
        self._vehicle: "Vehicle" = vehicle
        self._vehicle_type: VehicleType = vehicle.vehicle_type
        self._slot: "ParkingSlot"       = slot
        self._floor: "ParkingFloor"     = floor
        self._entry_time: datetime      = datetime.now()
        self._exit_time = None  # type: datetime | None
        self._status: str               = TicketStatus.ACTIVE
        self._fee_paid: float           = 0.0

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def vehicle_type(self) -> VehicleType:
        return self._vehicle_type

    @property
    def slot(self) -> "ParkingSlot":
        return self._slot

    @property
    def floor(self) -> "ParkingFloor":
        return self._floor

    @property
    def vehicle(self) -> "Vehicle":
        return self._vehicle

    @property
    def entry_time(self) -> datetime:
        return self._entry_time

    @property
    def exit_time(self) -> datetime | None:
        return self._exit_time

    @property
    def status(self) -> str:
        return self._status

    @property
    def fee_paid(self) -> float:
        return self._fee_paid

    def is_active(self) -> bool:
        return self._status == TicketStatus.ACTIVE

    # ------------------------------------------------------------------ #
    # Close ticket on exit
    # ------------------------------------------------------------------ #

    def close(self, exit_time: datetime, fee: float) -> None:
        """
        Mark the ticket as closed when the vehicle exits.

        Raises:
            ValueError: if ticket is already closed (prevents repeated exit).
        """
        if not self.is_active():
            raise ValueError(
                f"Ticket {self._ticket_id} is already CLOSED. "
                "Cannot process exit again."
            )
        self._exit_time = exit_time
        self._fee_paid  = fee
        self._status    = TicketStatus.CLOSED

    # ------------------------------------------------------------------ #
    # Display
    # ------------------------------------------------------------------ #

    def view_slots(self) -> None:
        """Display ticket details (mapped from UML's view_slots())."""
        print(self)

    def book_slot(self, vehicle_type: VehicleType) -> None:
        """
        Placeholder method as per UML interface.
        Actual booking is handled by ParkingService.
        """
        pass

    def __str__(self) -> str:
        lines = [
            "=" * 55,
            "          PARKING TICKET",
            "=" * 55,
            f"  Ticket ID    : {self._ticket_id}",
            f"  Vehicle No.  : {self._vehicle.number}",
            f"  Vehicle Type : {self._vehicle_type.value}",
            f"  Floor        : {self._floor.floor_number}",
            f"  Slot         : {self._slot.slot_number}",
            f"  Entry Time   : {self._entry_time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        if self._exit_time:
            duration = self._exit_time - self._entry_time
            hours    = duration.total_seconds() / 3600
            lines += [
                f"  Exit Time    : {self._exit_time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"  Duration     : {hours:.2f} hour(s)",
                f"  Fee Paid     : Rs.{self._fee_paid:.2f}",
                f"  Status       : {self._status}",
            ]
        else:
            lines.append(f"  Status       : {self._status}")
        lines.append("=" * 55)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Ticket(id={self._ticket_id}, status={self._status})"

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _generate_ticket_id() -> str:
        """Generate a short, readable unique ticket ID."""
        return "TKT-" + str(uuid.uuid4()).upper()[:8]
