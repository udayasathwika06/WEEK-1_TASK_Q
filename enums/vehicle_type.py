"""
VehicleType Enum
================
Defines the supported vehicle types in the parking lot.
Extending the system with a new vehicle type (e.g., BUS) only requires
adding a new member here — no if/else changes needed elsewhere.
"""

from enum import Enum, auto


class VehicleType(Enum):
    """Enum representing the types of vehicles supported by the parking lot."""
    BIKE = "BIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"

    def __str__(self) -> str:
        return self.value
