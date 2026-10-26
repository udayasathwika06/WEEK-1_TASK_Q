"""
Vehicle Models
==============
Abstract base class Vehicle and concrete subclasses Bike, Car, Truck.

Design Pattern: Template Method
  - Vehicle defines the interface and enforces the structure.
  - Subclasses provide concrete implementations without changing shared logic.
  - Adding a new vehicle type means creating a new subclass with zero changes
    to existing code (Open/Closed Principle).
"""

from abc import ABC, abstractmethod
from enums.vehicle_type import VehicleType


class Vehicle(ABC):
    """
    Abstract base class for all vehicles.
    Enforces that every vehicle has a number plate and a type.
    """

    def __init__(self, number: str) -> None:
        if not number or not number.strip():
            raise ValueError("Vehicle number plate cannot be empty.")
        self._number: str = number.strip().upper()
        self._vehicle_type: VehicleType = self._get_vehicle_type()

    @property
    def number(self) -> str:
        """Returns the vehicle's registration number."""
        return self._number

    @property
    def vehicle_type(self) -> VehicleType:
        """Returns the VehicleType enum value for this vehicle."""
        return self._vehicle_type

    @abstractmethod
    def _get_vehicle_type(self) -> VehicleType:
        """Template method: subclasses return their specific VehicleType."""
        pass

    def __str__(self) -> str:
        return f"{self._vehicle_type.value}({self._number})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(number='{self._number}')"


class Bike(Vehicle):
    """Represents a two-wheeled motorcycle or scooter."""

    def _get_vehicle_type(self) -> VehicleType:
        return VehicleType.BIKE


class Car(Vehicle):
    """Represents a standard passenger car."""

    def _get_vehicle_type(self) -> VehicleType:
        return VehicleType.CAR


class Truck(Vehicle):
    """Represents a heavy-duty truck or large commercial vehicle."""

    def _get_vehicle_type(self) -> VehicleType:
        return VehicleType.TRUCK
