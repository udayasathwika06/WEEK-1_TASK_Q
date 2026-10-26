"""
main.py - Driver Program
=========================
Demonstrates at least 8 normal and edge-case operations for the
Extensible Multi-Floor Parking Lot System.

Operations demonstrated:
  1.  Setup: Create parking lot with 2 floors and mixed slots
  2.  Park a BIKE successfully
  3.  Park a CAR successfully
  4.  Park a TRUCK successfully
  5.  [Edge] Duplicate vehicle parking attempt (same vehicle number)
  6.  View free slots by vehicle type (BIKE)
  7.  Display occupancy across all floors
  8.  Unpark a vehicle using ticket (calculate fee)
  9.  [Edge] Repeat exit using the same closed ticket
  10. [Edge] Invalid ticket ID for unpark
  11. Park more cars to fill up slots, then attempt to park when full
  12. Switch fee strategy at runtime (Hourly -> Flat) and unpark
  13. View all floors summary
  14. Exit the lot
"""

import sys
import time

# Fix Windows console encoding (CP1252 -> UTF-8)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from parking_lot import ParkingLot
from models.parking_floor import ParkingFloor
from models.parking_slot import ParkingSlot
from enums.vehicle_type import VehicleType
from services.parking_service import ParkingService, ParkingServiceError
from factories.strategy_factory import StrategyFactory


# =========================================================================== #
# Helper
# =========================================================================== #

def section(title: str) -> None:
    """Print a visual section separator for console output clarity."""
    width = 65
    print("\n+" + "=" * (width - 2) + "+")
    print("|  " + title.ljust(width - 4) + "|")
    print("+" + "=" * (width - 2) + "+")


def try_operation(label: str, fn) -> None:
    """Execute fn() and catch ParkingServiceError gracefully."""
    print(f"\n>>> {label}")
    try:
        fn()
    except ParkingServiceError as e:
        print(f"[ERROR] {e}")
    except ValueError as e:
        print(f"[ERROR] {e}")


# =========================================================================== #
# Setup: Build the parking lot structure
# =========================================================================== #

def setup_parking_lot() -> ParkingLot:
    """
    Create a 2-floor parking lot:
      Floor 1: 3 BIKE slots, 3 CAR slots, 2 TRUCK slots
      Floor 2: 2 BIKE slots, 4 CAR slots, 1 TRUCK slot
    """
    lot = ParkingLot.get_instance("Skyline Multi-Floor Parking")

    # ---- Floor 1 ----
    floor1 = ParkingFloor(1)
    floor1.add_slots([
        ParkingSlot(101, VehicleType.BIKE),
        ParkingSlot(102, VehicleType.BIKE),
        ParkingSlot(103, VehicleType.BIKE),
        ParkingSlot(104, VehicleType.CAR),
        ParkingSlot(105, VehicleType.CAR),
        ParkingSlot(106, VehicleType.CAR),
        ParkingSlot(107, VehicleType.TRUCK),
        ParkingSlot(108, VehicleType.TRUCK),
    ])
    lot.add_floor(floor1)

    # ---- Floor 2 ----
    floor2 = ParkingFloor(2)
    floor2.add_slots([
        ParkingSlot(201, VehicleType.BIKE),
        ParkingSlot(202, VehicleType.BIKE),
        ParkingSlot(203, VehicleType.CAR),
        ParkingSlot(204, VehicleType.CAR),
        ParkingSlot(205, VehicleType.CAR),
        ParkingSlot(206, VehicleType.CAR),
        ParkingSlot(207, VehicleType.TRUCK),
    ])
    lot.add_floor(floor2)

    return lot


# =========================================================================== #
# Main driver
# =========================================================================== #

def main() -> None:
    # -------------------------------------------------------------------
    # Operation 1: Setup
    # -------------------------------------------------------------------
    section("OPERATION 1: Setup Parking Lot")
    lot = setup_parking_lot()
    lot.view_floors()

    # Create service with default Hourly fee strategy
    service = ParkingService(lot=lot)
    print("[INFO] ParkingService initialised with HourlyFeeStrategy.")

    # -------------------------------------------------------------------
    # Operation 2: Park a BIKE
    # -------------------------------------------------------------------
    section("OPERATION 2: Park a BIKE")
    bike_ticket = None
    try_operation("Park BIKE KA-01-HH-1111", lambda: None)  # dry-run label
    try:
        bike_ticket = service.park_vehicle(VehicleType.BIKE, "KA-01-HH-1111")
    except ParkingServiceError as e:
        print(f"[ERROR] {e}")

    # -------------------------------------------------------------------
    # Operation 3: Park a CAR
    # -------------------------------------------------------------------
    section("OPERATION 3: Park a CAR")
    car_ticket = None
    try:
        car_ticket = service.park_vehicle(VehicleType.CAR, "MH-12-AB-5678")
    except ParkingServiceError as e:
        print(f"[ERROR] {e}")

    # -------------------------------------------------------------------
    # Operation 4: Park a TRUCK
    # -------------------------------------------------------------------
    section("OPERATION 4: Park a TRUCK")
    truck_ticket = None
    try:
        truck_ticket = service.park_vehicle(VehicleType.TRUCK, "DL-09-ZZ-9999")
    except ParkingServiceError as e:
        print(f"[ERROR] {e}")

    # -------------------------------------------------------------------
    # Operation 5: [Edge Case] Duplicate Vehicle Parking
    # -------------------------------------------------------------------
    section("OPERATION 5 [EDGE]: Duplicate Vehicle Parking Attempt")
    try_operation(
        "Attempt to park KA-01-HH-1111 AGAIN",
        lambda: service.park_vehicle(VehicleType.BIKE, "KA-01-HH-1111")
    )

    # -------------------------------------------------------------------
    # Operation 6: View Free Slots by Vehicle Type
    # -------------------------------------------------------------------
    section("OPERATION 6: View Free Slots by Vehicle Type")
    print("\n-- Free BIKE slots --")
    service.view_free_slots(VehicleType.BIKE)
    print("\n-- Free CAR slots --")
    service.view_free_slots(VehicleType.CAR)
    print("\n-- Free TRUCK slots --")
    service.view_free_slots(VehicleType.TRUCK)

    # -------------------------------------------------------------------
    # Operation 7: Display Occupancy
    # -------------------------------------------------------------------
    section("OPERATION 7: Display Occupancy")
    service.display_occupancy()

    # -------------------------------------------------------------------
    # Operation 8: Unpark Vehicle (BIKE exits, fee calculated)
    # -------------------------------------------------------------------
    section("OPERATION 8: Unpark BIKE - Calculate Fee")
    if bike_ticket:
        # Small sleep so duration > 0s and we see real fee
        time.sleep(1)
        try:
            fee = service.unpark_vehicle(bike_ticket.ticket_id)
            print(f"[INFO] Fee collected: Rs.{fee:.2f}")
        except ParkingServiceError as e:
            print(f"[ERROR] {e}")

    # -------------------------------------------------------------------
    # Operation 9: [Edge Case] Repeated Exit (same closed ticket)
    # -------------------------------------------------------------------
    section("OPERATION 9 [EDGE]: Repeated Exit on Closed Ticket")
    if bike_ticket:
        try_operation(
            f"Attempt to exit again with ticket {bike_ticket.ticket_id}",
            lambda: service.unpark_vehicle(bike_ticket.ticket_id)
        )

    # -------------------------------------------------------------------
    # Operation 10: [Edge Case] Invalid Ticket ID
    # -------------------------------------------------------------------
    section("OPERATION 10 [EDGE]: Unpark with Invalid Ticket ID")
    try_operation(
        "Unpark with 'TKT-INVALID99'",
        lambda: service.unpark_vehicle("TKT-INVALID99")
    )

    # -------------------------------------------------------------------
    # Operation 11: [Edge Case] Fill all CAR slots then try to park one more
    # -------------------------------------------------------------------
    section("OPERATION 11 [EDGE]: Fill All CAR Slots - Then Attempt Overflow")
    extra_car_tickets = []
    car_plates = ["TN-01-AA-0001", "TN-01-AA-0002", "TN-01-AA-0003",
                  "TN-01-AA-0004", "TN-01-AA-0005", "TN-01-AA-0006"]
    # Floor1 has 3 CAR slots (one already occupied by MH-12-AB-5678)
    # Floor2 has 4 CAR slots -> 6 remaining free slots
    for plate in car_plates:
        try:
            t = service.park_vehicle(VehicleType.CAR, plate)
            extra_car_tickets.append(t)
        except ParkingServiceError as e:
            print(f"[INFO] Could not park {plate}: {e}")

    print("\n-- Attempting to park one MORE CAR when lot is full --")
    try_operation(
        "Park CAR TN-01-AA-OVERFLOW",
        lambda: service.park_vehicle(VehicleType.CAR, "TN-01-AA-OVERFLOW")
    )

    # -------------------------------------------------------------------
    # Operation 12: Switch Fee Strategy - Flat Fee - then Unpark TRUCK
    # -------------------------------------------------------------------
    section("OPERATION 12: Switch to FlatFeeStrategy - Unpark TRUCK")
    flat_strategy = StrategyFactory.get_fee_strategy("flat")
    service.set_fee_strategy(flat_strategy)

    if truck_ticket:
        time.sleep(1)
        try:
            fee = service.unpark_vehicle(truck_ticket.ticket_id)
            print(f"[INFO] Flat fee collected: Rs.{fee:.2f}")
        except ParkingServiceError as e:
            print(f"[ERROR] {e}")

    # -------------------------------------------------------------------
    # Operation 13: View all floors after activity
    # -------------------------------------------------------------------
    section("OPERATION 13: View All Floors Summary")
    lot.view_floors()

    # -------------------------------------------------------------------
    # Operation 14: Exit the Lot
    # -------------------------------------------------------------------
    section("OPERATION 14: Close / Exit the Parking Lot")
    lot.exit_lot()


# =========================================================================== #
# Entry Point
# =========================================================================== #

if __name__ == "__main__":
    main()
