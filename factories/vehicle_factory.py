"""
Vehicle Factory
===============
Design Pattern: Factory Method
  - Decouples object creation from the rest of the application.
  - ParkingService never uses `if vehicle_type == BIKE: return Bike(...)`.
  - Adding a new vehicle type only requires:
    1. Adding the enum member to VehicleType
    2. Creating the subclass in models/vehicle.py
    3. Registering it in VehicleFactory._REGISTRY
    No other code changes needed.
"""

from enums.vehicle_type import VehicleType
from models.vehicle import Bike, Car, Truck, Vehicle
from typing import Type, Dict


class VehicleFactory:
    """
    Factory for creating Vehicle instances.

    Usage:
        vehicle = VehicleFactory.create(VehicleType.CAR, "KA-01-HH-1234")
    """

    # Registry maps VehicleType -> Vehicle subclass
    _REGISTRY: Dict[VehicleType, Type[Vehicle]] = {
        VehicleType.BIKE:  Bike,
        VehicleType.CAR:   Car,
        VehicleType.TRUCK: Truck,
    }

    @classmethod
    def create(cls, vehicle_type: VehicleType, number: str) -> Vehicle:
        """
        Instantiate the correct Vehicle subclass.

        Args:
            vehicle_type: Enum member indicating which vehicle to create.
            number:       Registration plate of the vehicle.

        Returns:
            An instance of the appropriate Vehicle subclass.

        Raises:
            ValueError: if vehicle_type is not registered.
        """
        vehicle_class = cls._REGISTRY.get(vehicle_type)
        if vehicle_class is None:
            raise ValueError(
                f"Unsupported vehicle type: {vehicle_type}. "
                f"Supported types: {list(cls._REGISTRY.keys())}"
            )
        return vehicle_class(number)

    @classmethod
    def register(cls, vehicle_type: VehicleType, vehicle_class: Type[Vehicle]) -> None:
        """
        Register a new vehicle type at runtime (extensibility hook).

        Args:
            vehicle_type:  New VehicleType enum member.
            vehicle_class: Corresponding Vehicle subclass.
        """
        cls._REGISTRY[vehicle_type] = vehicle_class

    @classmethod
    def supported_types(cls) -> list:
        """Returns the list of currently supported VehicleType members."""
        return list(cls._REGISTRY.keys())
