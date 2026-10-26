# Extensible Multi-Floor Parking Lot System

A **console-based parking lot application** built with clean OOP principles, multiple design patterns, and full extensibility — implemented in **Python 3.8+**.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [UML / Class Diagram](#uml--class-diagram)
3. [Design Decisions](#design-decisions)
4. [Design Patterns Used](#design-patterns-used)
5. [How to Run](#how-to-run)
6. [Sample Console Output](#sample-console-output)
7. [Test Cases](#test-cases)
8. [Extensibility Guide](#extensibility-guide)

---

## Project Structure

```
parking-lot/
├── enums/
│   ├── __init__.py
│   └── vehicle_type.py          # VehicleType enum: BIKE, CAR, TRUCK
├── models/
│   ├── __init__.py
│   ├── vehicle.py               # Abstract Vehicle + Bike, Car, Truck
│   ├── parking_slot.py          # ParkingSlot (slot_number, slot_type, slot_status)
│   ├── parking_floor.py         # ParkingFloor (manages list of ParkingSlots)
│   └── ticket.py                # Ticket (entry_time, status, fee_paid)
├── strategies/
│   ├── __init__.py
│   ├── fee_strategy.py          # FeeStrategy ABC + HourlyFeeStrategy, FlatFeeStrategy
│   └── slot_allocation.py       # SlotAllocationStrategy ABC + FirstAvailableStrategy
├── factories/
│   ├── __init__.py
│   ├── vehicle_factory.py       # VehicleFactory (registry-based)
│   └── strategy_factory.py      # StrategyFactory (fee + slot strategies)
├── services/
│   ├── __init__.py
│   └── parking_service.py       # ParkingService — orchestrates all business logic
├── parking_lot.py               # ParkingLot (Singleton)
├── main.py                      # Driver program (14 operations, 5+ edge cases)
├── tests/
│   ├── __init__.py
│   └── test_parking_lot.py      # 12 unit/functional test cases
└── README.md
```

---

## UML / Class Diagram

```
┌─────────────────────┐
│     VehicleType     │  <<enum>>
│─────────────────────│
│  BIKE               │
│  CAR                │
│  TRUCK              │
└─────────────────────┘
          ▲
          │ uses
┌─────────────────────┐        ┌─────────────────────┐
│      Vehicle        │        │     ParkingSlot      │
│─────────────────────│        │─────────────────────-│
│ -number: str        │        │ -slot_number: int    │
│ -vehicle_type: Enum │        │ -slot_type: VehicleType│
│─────────────────────│        │ -slot_status: str    │
│ +number             │        │─────────────────────-│
│ +vehicle_type       │        │ +is_available()      │
│ +_get_vehicle_type()│        │ +book_slot(vehicle)  │
└─────────────────────┘        │ +vacate_slot()       │
    ▲      ▲      ▲            │ +get_vehicle()       │
    │      │      │            └─────────────────────-┘
  Bike    Car  Truck                    │ 1..*
                                        │
                           ┌────────────▼─────────────┐
                           │      ParkingFloor         │
                           │──────────────────────────-│
                           │ -floor_number: int        │
                           │ -floor_status: str        │
                           │──────────────────────────-│
                           │ +add_slot(slot)           │
                           │ +available_slots(type)    │
                           │ +get_available_slot(type) │
                           │ +view_slots(type)         │
                           │ +books_slot(slot, vehicle)│
                           └────────────▲─────────────┘
                                        │ 1..*
                           ┌────────────┴─────────────┐
                           │       ParkingLot          │  <<Singleton>>
                           │──────────────────────────-│
                           │ -name: str                │
                           │ -floors: Dict             │
                           │──────────────────────────-│
                           │ +get_instance()           │
                           │ +add_floor(floor)         │
                           │ +view_floors()            │
                           │ +display_occupancy()      │
                           │ +exit_lot()               │
                           └──────────────────────────-┘

┌──────────────────────────┐
│         Ticket           │
│──────────────────────────│
│ -ticket_id: str          │
│ -vehicle_type: VehicleType│
│ -slot: ParkingSlot       │
│ -floor: ParkingFloor     │
│ -entry_time: datetime    │
│ -status: str             │
│ -fee_paid: float         │
│──────────────────────────│
│ +is_active(): bool       │
│ +close(exit_time, fee)   │
│ +view_slots()            │
└──────────────────────────┘

┌──────────────────────────┐         ┌───────────────────────────┐
│      FeeStrategy         │<<ABC>>  │   SlotAllocationStrategy  │<<ABC>>
│──────────────────────────│         │───────────────────────────│
│ +calculate_fee(...)      │         │ +allocate(floors, type)   │
└──────────────────────────┘         └───────────────────────────┘
     ▲              ▲                          ▲
     │              │                          │
HourlyFee      FlatFee               FirstAvailableStrategy
Strategy       Strategy

┌──────────────────────────────────────────────────────┐
│                   ParkingService                     │
│──────────────────────────────────────────────────────│
│ -lot: ParkingLot                                     │
│ -fee_strategy: FeeStrategy                           │
│ -slot_strategy: SlotAllocationStrategy               │
│ -tickets: Dict[str, Ticket]                          │
│ -parked_vehicles: Dict[str, str]                     │
│──────────────────────────────────────────────────────│
│ +park_vehicle(type, number) -> Ticket                │
│ +unpark_vehicle(ticket_id) -> float                  │
│ +view_free_slots(type)                               │
│ +display_occupancy()                                 │
│ +set_fee_strategy(strategy)                          │
│ +set_slot_strategy(strategy)                         │
└──────────────────────────────────────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│   VehicleFactory     │       │   StrategyFactory    │
│──────────────────────│       │──────────────────────│
│ +create(type, number)│       │ +get_fee_strategy()  │
│ +register(type, cls) │       │ +get_slot_strategy() │
└──────────────────────┘       └──────────────────────┘
```

---

## Design Decisions

### 1. Why Enums for Vehicle Types?
Using `VehicleType` as an enum eliminates magic strings scattered throughout the code. Comparisons are type-safe, IDE-friendly, and adding a new type is a single-line change in one file.

### 2. Abstract Base Classes Instead of if/else Chains
`Vehicle`, `FeeStrategy`, and `SlotAllocationStrategy` use ABCs and polymorphism. The `ParkingService` never writes `if vehicle_type == "BIKE": rate = 10`. Instead, it calls `strategy.calculate_fee(...)` — the object itself knows what to do. This is the **Open/Closed Principle** in action.

### 3. Separated Layers
| Layer | Responsibility |
|-------|---------------|
| **Enums** | Named constants — no magic strings |
| **Models** | Pure domain objects, no business logic |
| **Strategies** | Interchangeable algorithms |
| **Factories** | Object creation centralised |
| **ParkingLot** | Structural management |
| **ParkingService** | Orchestration + validation |
| **main.py** | Driver / UI |

This separation makes each layer independently testable and replaceable.

### 4. Ticket as the Source of Truth
The ticket holds a direct reference to the `ParkingSlot` and `ParkingFloor`. On exit, the service simply calls `ticket.slot.vacate_slot()` — no floor/slot scanning needed.

### 5. Duplicate Detection
`ParkingService` maintains a `_parked_vehicles` dict (`vehicle_number → ticket_id`). Parking the same number plate twice immediately raises a `ParkingServiceError`.

### 6. Repeated-Exit Prevention
`Ticket.close()` checks the ticket status and raises `ValueError` if already closed. `ParkingService.unpark_vehicle()` also validates before calling `close()`.

---

## Design Patterns Used

### Pattern 1: Strategy Pattern
**Where**: `FeeStrategy`, `SlotAllocationStrategy`

**Purpose**: Separates the *algorithm* from the *context* that uses it. The `ParkingService` holds a reference to a strategy interface and delegates calculation/allocation to it. Swapping strategies (e.g., from hourly to flat pricing) requires zero code changes — just call `service.set_fee_strategy(new_strategy)` at runtime.

```python
# Runtime swap — no code changes, no if/else:
service.set_fee_strategy(StrategyFactory.get_fee_strategy("flat"))
fee = service.unpark_vehicle(ticket_id)
```

### Pattern 2: Factory Method Pattern
**Where**: `VehicleFactory`, `StrategyFactory`

**Purpose**: Decouples object creation from usage. The `ParkingService` never writes `Bike(...)` or `Car(...)` directly — it calls `VehicleFactory.create(vehicle_type, number)`. The factory consults its **registry** and returns the right subclass. Adding a new vehicle type requires only:
1. A new enum member
2. A new subclass
3. One `_REGISTRY` entry

```python
# Adding BUS type — zero changes to ParkingService:
VehicleFactory.register(VehicleType.BUS, Bus)
```

### Pattern 3: Singleton Pattern
**Where**: `ParkingLot`

**Purpose**: Ensures exactly one `ParkingLot` instance exists application-wide. All service components share the same lot state without passing it explicitly everywhere.

### Pattern 4: Template Method Pattern
**Where**: `Vehicle` base class

**Purpose**: Defines the algorithm skeleton (constructor sets `number` and calls `_get_vehicle_type()`), leaving the specific vehicle-type decision to each subclass. Enforces consistent structure without code duplication.

---

## How to Run

### Prerequisites
- Python 3.8+
- No external dependencies required

### Run the Driver Program
```bash
cd parking-lot
python main.py
```

### Run All Tests
```bash
# Using unittest (built-in):
python -m unittest discover -s tests -v

# Or using pytest (if installed):
python -m pytest tests/ -v
```

---

## Sample Console Output

```
╔═══════════════════════════════════════════════════════════════╗
║  OPERATION 1: Setup Parking Lot                               ║
╚═══════════════════════════════════════════════════════════════╝
[INFO] Floor 1 added to 'Skyline Multi-Floor Parking'.
[INFO] Floor 2 added to 'Skyline Multi-Floor Parking'.

============================================================
  PARKING LOT: Skyline Multi-Floor Parking
  Total Floors: 2
============================================================
  Floor 1 | Status: OPEN | Slots: 8 total, 8 available
  Floor 2 | Status: OPEN | Slots: 7 total, 7 available
============================================================

╔═══════════════════════════════════════════════════════════════╗
║  OPERATION 2: Park a BIKE                                     ║
╚═══════════════════════════════════════════════════════════════╝

[SUCCESS] Vehicle 'KA-01-HH-1111' parked successfully.
=======================================================
          PARKING TICKET
=======================================================
  Ticket ID    : TKT-A1B2C3D4
  Vehicle No.  : KA-01-HH-1111
  Vehicle Type : BIKE
  Floor        : 1
  Slot         : 101
  Entry Time   : 2025-01-01 10:00:00
  Status       : ACTIVE
=======================================================

╔═══════════════════════════════════════════════════════════════╗
║  OPERATION 5 [EDGE]: Duplicate Vehicle Parking Attempt        ║
╚═══════════════════════════════════════════════════════════════╝
>>> Attempt to park KA-01-HH-1111 AGAIN
[ERROR] Vehicle 'KA-01-HH-1111' is already parked. Ticket: TKT-A1B2C3D4

╔═══════════════════════════════════════════════════════════════╗
║  OPERATION 9 [EDGE]: Repeated Exit on Closed Ticket           ║
╚═══════════════════════════════════════════════════════════════╝
[ERROR] Ticket 'TKT-A1B2C3D4' has already been processed. Repeated exit is not allowed.

╔═══════════════════════════════════════════════════════════════╗
║  OPERATION 10 [EDGE]: Unpark with Invalid Ticket ID           ║
╚═══════════════════════════════════════════════════════════════╝
[ERROR] Ticket 'TKT-INVALID99' not found. Please provide a valid ticket.
```

---

## Test Cases

| # | Test Class | Test Name | What It Verifies |
|---|-----------|-----------|-----------------|
| TC-01 | `TestVehicleFactory` | `test_create_bike/car/truck` | Factory returns correct subclass |
| TC-02 | `TestVehicleFactory` | `test_invalid_vehicle_number_raises` | Empty plate raises ValueError |
| TC-03 | `TestParkingSlot` | `test_book_slot_marks_occupied` | Slot status changes on booking |
| TC-04 | `TestParkingSlot` | `test_double_book_raises` | Double-booking raises ValueError |
| TC-05 | `TestParkingSlot` | `test_vacate_slot` | Slot available after vacate |
| TC-06 | `TestFeeStrategies` | `test_hourly_fee_*` | Hourly rate calculations |
| TC-07 | `TestFeeStrategies` | `test_flat_fee_*` | Flat fee per vehicle type |
| TC-08 | `TestDuplicateParking` | `test_duplicate_vehicle_raises_error` | Same plate rejected |
| TC-09 | `TestRepeatedExit` | `test_second_unpark_raises_error` | Closed ticket raises error |
| TC-10 | `TestInvalidTicket` | `test_invalid_ticket_raises_error` | Unknown ticket ID rejected |
| TC-11 | `TestNoAvailableSlots` | `test_park_when_full_raises_error` | Overflow parking rejected |
| TC-12 | `TestStrategySwitch` | `test_switch_to_flat_fee` | Runtime strategy swap works |

---

## Extensibility Guide

### Adding a New Vehicle Type (e.g., BUS)

1. **`enums/vehicle_type.py`** — add `BUS = "BUS"`
2. **`models/vehicle.py`** — add `class Bus(Vehicle): ...`
3. **`factories/vehicle_factory.py`** — add `VehicleType.BUS: Bus` to `_REGISTRY`
4. **`strategies/fee_strategy.py`** — add `VehicleType.BUS: 80.0` to each strategy's rate dict
5. No changes needed in `ParkingService`, `ParkingFloor`, or `Ticket` ✅

### Adding a New Pricing Strategy (e.g., Weekend Rate)

1. Create `class WeekendFeeStrategy(FeeStrategy)` in `strategies/fee_strategy.py`
2. Register it: `StrategyFactory.register_fee_strategy("weekend", WeekendFeeStrategy)`
3. Switch at runtime: `service.set_fee_strategy(StrategyFactory.get_fee_strategy("weekend"))`
4. No other code changes needed ✅

### Adding a New Slot Allocation Strategy (e.g., Nearest Entrance)

1. Create `class NearestEntranceStrategy(SlotAllocationStrategy)` in `strategies/slot_allocation.py`
2. Register and inject via `StrategyFactory`
3. No changes to `ParkingService` or models ✅
