"""
test_parking_lot.py — Unit & Functional Test Suite
====================================================
Covers 12 test cases across all major components.

Run with:
    python -m pytest tests/ -v
  or:
    python -m unittest discover -s tests -v
"""

import unittest
from datetime import datetime, timedelta

# ---- Reset singleton between tests ----
from parking_lot import ParkingLot
from models.parking_floor import ParkingFloor
from models.parking_slot import ParkingSlot, SlotStatus
from models.vehicle import Bike, Car, Truck
from models.ticket import Ticket, TicketStatus
from enums.vehicle_type import VehicleType
from factories.vehicle_factory import VehicleFactory
from factories.strategy_factory import StrategyFactory
from strategies.fee_strategy import HourlyFeeStrategy, FlatFeeStrategy
from services.parking_service import ParkingService, ParkingServiceError


def build_lot(name: str = "Test Lot") -> ParkingLot:
    """Helper: build a small but complete parking lot for testing."""
    ParkingLot.reset()
    lot = ParkingLot.get_instance(name)

    floor1 = ParkingFloor(1)
    floor1.add_slots([
        ParkingSlot(101, VehicleType.BIKE),
        ParkingSlot(102, VehicleType.CAR),
        ParkingSlot(103, VehicleType.TRUCK),
    ])
    lot.add_floor(floor1)

    floor2 = ParkingFloor(2)
    floor2.add_slots([
        ParkingSlot(201, VehicleType.BIKE),
        ParkingSlot(202, VehicleType.CAR),
    ])
    lot.add_floor(floor2)

    return lot


# =========================================================================== #
# TC-01: Vehicle Factory creates correct subclasses
# =========================================================================== #

class TestVehicleFactory(unittest.TestCase):

    def test_create_bike(self):
        vehicle = VehicleFactory.create(VehicleType.BIKE, "KA-01-HH-1111")
        self.assertIsInstance(vehicle, Bike)
        self.assertEqual(vehicle.vehicle_type, VehicleType.BIKE)
        self.assertEqual(vehicle.number, "KA-01-HH-1111")

    def test_create_car(self):
        vehicle = VehicleFactory.create(VehicleType.CAR, "MH-12-AB-5678")
        self.assertIsInstance(vehicle, Car)
        self.assertEqual(vehicle.vehicle_type, VehicleType.CAR)

    def test_create_truck(self):
        vehicle = VehicleFactory.create(VehicleType.TRUCK, "DL-09-ZZ-9999")
        self.assertIsInstance(vehicle, Truck)
        self.assertEqual(vehicle.vehicle_type, VehicleType.TRUCK)

    def test_invalid_vehicle_number_raises(self):
        with self.assertRaises(ValueError):
            VehicleFactory.create(VehicleType.CAR, "   ")


# =========================================================================== #
# TC-02: ParkingSlot — booking and vacating
# =========================================================================== #

class TestParkingSlot(unittest.TestCase):

    def setUp(self):
        self.slot = ParkingSlot(101, VehicleType.CAR)
        self.vehicle = Car("MH-12-AB-0001")

    def test_slot_initially_available(self):
        self.assertTrue(self.slot.is_available())
        self.assertEqual(self.slot.slot_status, SlotStatus.AVAILABLE)

    def test_book_slot_marks_occupied(self):
        self.slot.book_slot(self.vehicle)
        self.assertFalse(self.slot.is_available())
        self.assertEqual(self.slot.slot_status, SlotStatus.OCCUPIED)
        self.assertEqual(self.slot.get_vehicle(), self.vehicle)

    def test_double_book_raises(self):
        self.slot.book_slot(self.vehicle)
        with self.assertRaises(ValueError):
            self.slot.book_slot(self.vehicle)

    def test_vacate_slot(self):
        self.slot.book_slot(self.vehicle)
        self.slot.vacate_slot()
        self.assertTrue(self.slot.is_available())
        self.assertIsNone(self.slot.get_vehicle())

    def test_vacate_already_empty_raises(self):
        with self.assertRaises(ValueError):
            self.slot.vacate_slot()


# =========================================================================== #
# TC-03: Fee Strategy — correct calculations
# =========================================================================== #

class TestFeeStrategies(unittest.TestCase):

    def test_hourly_fee_bike_one_hour(self):
        strategy = HourlyFeeStrategy()
        entry = datetime(2025, 1, 1, 10, 0, 0)
        exit_ = datetime(2025, 1, 1, 11, 0, 0)
        fee = strategy.calculate_fee(entry, exit_, VehicleType.BIKE)
        self.assertAlmostEqual(fee, 10.0)

    def test_hourly_fee_car_two_hours(self):
        strategy = HourlyFeeStrategy()
        entry = datetime(2025, 1, 1, 9, 0, 0)
        exit_ = datetime(2025, 1, 1, 11, 0, 0)
        fee = strategy.calculate_fee(entry, exit_, VehicleType.CAR)
        self.assertAlmostEqual(fee, 40.0)

    def test_hourly_fee_truck_minimum_one_hour(self):
        # Even if parked for 10 seconds, minimum is 1 hour
        strategy = HourlyFeeStrategy()
        entry = datetime(2025, 1, 1, 10, 0, 0)
        exit_ = datetime(2025, 1, 1, 10, 0, 10)  # 10 seconds
        fee = strategy.calculate_fee(entry, exit_, VehicleType.TRUCK)
        self.assertAlmostEqual(fee, 50.0)

    def test_flat_fee_bike(self):
        strategy = FlatFeeStrategy()
        entry = datetime(2025, 1, 1, 8, 0, 0)
        exit_ = datetime(2025, 1, 1, 20, 0, 0)  # 12 hours — doesn't matter
        fee = strategy.calculate_fee(entry, exit_, VehicleType.BIKE)
        self.assertAlmostEqual(fee, 30.0)

    def test_flat_fee_truck(self):
        strategy = FlatFeeStrategy()
        entry = datetime(2025, 1, 1, 8, 0, 0)
        exit_ = datetime(2025, 1, 1, 20, 0, 0)
        fee = strategy.calculate_fee(entry, exit_, VehicleType.TRUCK)
        self.assertAlmostEqual(fee, 150.0)


# =========================================================================== #
# TC-04: Park Vehicle — happy path
# =========================================================================== #

class TestParkVehicle(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_park_bike_issues_ticket(self):
        ticket = self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-0001")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle_type, VehicleType.BIKE)
        self.assertTrue(ticket.is_active())

    def test_park_car_occupies_slot(self):
        ticket = self.service.park_vehicle(VehicleType.CAR, "MH-04-C-0001")
        self.assertFalse(ticket.slot.is_available())
        self.assertEqual(ticket.slot.get_vehicle().number, "MH-04-C-0001")

    def test_park_truck(self):
        ticket = self.service.park_vehicle(VehicleType.TRUCK, "DL-11-T-0001")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle_type, VehicleType.TRUCK)


# =========================================================================== #
# TC-05: [Edge] Duplicate vehicle parking
# =========================================================================== #

class TestDuplicateParking(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_duplicate_vehicle_raises_error(self):
        self.service.park_vehicle(VehicleType.CAR, "KA-99-AA-1234")
        with self.assertRaises(ParkingServiceError):
            self.service.park_vehicle(VehicleType.CAR, "KA-99-AA-1234")

    def test_case_insensitive_duplicate_check(self):
        self.service.park_vehicle(VehicleType.BIKE, "ka-99-bb-1234")
        with self.assertRaises(ParkingServiceError):
            self.service.park_vehicle(VehicleType.BIKE, "KA-99-BB-1234")


# =========================================================================== #
# TC-06: Unpark Vehicle — happy path
# =========================================================================== #

class TestUnparkVehicle(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_unpark_releases_slot(self):
        ticket = self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-0010")
        slot = ticket.slot
        self.service.unpark_vehicle(ticket.ticket_id)
        self.assertTrue(slot.is_available())

    def test_unpark_closes_ticket(self):
        ticket = self.service.park_vehicle(VehicleType.CAR, "MH-01-C-0010")
        self.service.unpark_vehicle(ticket.ticket_id)
        self.assertEqual(ticket.status, TicketStatus.CLOSED)
        self.assertIsNotNone(ticket.exit_time)

    def test_unpark_returns_positive_fee(self):
        ticket = self.service.park_vehicle(VehicleType.TRUCK, "DL-01-T-0010")
        fee = self.service.unpark_vehicle(ticket.ticket_id)
        self.assertGreaterEqual(fee, 50.0)  # minimum 1 hour * ₹50


# =========================================================================== #
# TC-07: [Edge] Repeated Exit (closed ticket)
# =========================================================================== #

class TestRepeatedExit(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_second_unpark_raises_error(self):
        ticket = self.service.park_vehicle(VehicleType.BIKE, "KA-55-B-0001")
        self.service.unpark_vehicle(ticket.ticket_id)
        with self.assertRaises(ParkingServiceError):
            self.service.unpark_vehicle(ticket.ticket_id)


# =========================================================================== #
# TC-08: [Edge] Invalid Ticket ID
# =========================================================================== #

class TestInvalidTicket(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_invalid_ticket_raises_error(self):
        with self.assertRaises(ParkingServiceError):
            self.service.unpark_vehicle("TKT-DOESNOTEXIST")


# =========================================================================== #
# TC-09: [Edge] No Available Slots (lot full for that type)
# =========================================================================== #

class TestNoAvailableSlots(unittest.TestCase):

    def setUp(self):
        # Lot with only 1 BIKE slot
        ParkingLot.reset()
        self.lot = ParkingLot.get_instance("Tiny Lot")
        floor1 = ParkingFloor(1)
        floor1.add_slot(ParkingSlot(101, VehicleType.BIKE))
        self.lot.add_floor(floor1)
        self.service = ParkingService(lot=self.lot)

    def test_park_when_full_raises_error(self):
        self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-FULL1")
        with self.assertRaises(ParkingServiceError):
            self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-FULL2")

    def test_no_slot_for_car_in_bike_only_lot(self):
        with self.assertRaises(ParkingServiceError):
            self.service.park_vehicle(VehicleType.CAR, "MH-01-C-NOSLOT")


# =========================================================================== #
# TC-10: Strategy Switch at Runtime
# =========================================================================== #

class TestStrategySwitch(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_switch_to_flat_fee(self):
        ticket = self.service.park_vehicle(VehicleType.TRUCK, "DL-01-T-FLAT")
        flat = StrategyFactory.get_fee_strategy("flat")
        self.service.set_fee_strategy(flat)
        fee = self.service.unpark_vehicle(ticket.ticket_id)
        self.assertAlmostEqual(fee, 150.0)  # FlatFeeStrategy.FLAT_FEES[TRUCK]

    def test_switch_back_to_hourly(self):
        flat = StrategyFactory.get_fee_strategy("flat")
        self.service.set_fee_strategy(flat)
        hourly = StrategyFactory.get_fee_strategy("hourly")
        self.service.set_fee_strategy(hourly)
        ticket = self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-HOURLY")
        fee = self.service.unpark_vehicle(ticket.ticket_id)
        self.assertGreaterEqual(fee, 10.0)


# =========================================================================== #
# TC-11: Parking Lot Singleton
# =========================================================================== #

class TestParkingLotSingleton(unittest.TestCase):

    def test_same_instance_returned(self):
        ParkingLot.reset()
        lot1 = ParkingLot.get_instance("Lot A")
        lot2 = ParkingLot.get_instance("Lot B")
        self.assertIs(lot1, lot2)

    def test_duplicate_floor_raises(self):
        ParkingLot.reset()
        lot = ParkingLot.get_instance("Singleton Lot")
        floor = ParkingFloor(1)
        lot.add_floor(floor)
        with self.assertRaises(ValueError):
            lot.add_floor(ParkingFloor(1))


# =========================================================================== #
# TC-12: Slot released after unpark allows re-parking
# =========================================================================== #

class TestSlotReuseAfterUnpark(unittest.TestCase):

    def setUp(self):
        self.lot = build_lot()
        self.service = ParkingService(lot=self.lot)

    def test_slot_reusable_after_vacate(self):
        # Park vehicle A
        t1 = self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-REUSE1")
        slot_number = t1.slot.slot_number
        # Unpark vehicle A
        self.service.unpark_vehicle(t1.ticket_id)
        # Slot should now be available
        self.assertTrue(t1.slot.is_available())
        # Park vehicle B — it should get the same freed slot
        t2 = self.service.park_vehicle(VehicleType.BIKE, "KA-01-B-REUSE2")
        self.assertEqual(t2.slot.slot_number, slot_number)


# =========================================================================== #
# Entry Point
# =========================================================================== #

if __name__ == "__main__":
    unittest.main(verbosity=2)
