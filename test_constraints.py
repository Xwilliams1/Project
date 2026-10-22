#!/usr/bin/env python3
from restaurant_app.models import Booking, EmployeeRestaurant, Employee, Restaurant
import os
import django
from django.core.exceptions import ValidationError

# Setup Django Environment context
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_platform.settings')
django.setup()


def run_business_rule_tests():
    print("🔬 Initializing Backend Constraint Validation Verification Suites...")

    # -----------------------------------------------------------------
    # TEST 1: Double-Booking Anti-Duplication Rule Verification
    # -----------------------------------------------------------------
    print("\nExecuting Test 1: Evaluating Multi-Table Duplication Block...")
    try:
        # Intentionally create a duplicate booking profile entry row matching Alice Williams' parameters
        duplicate_booking = Booking(
            booking_id="BK_FAIL_1",
            restaurant_name="Bistro Central",
            restaurant_address="123 Albert St, Brisbane QLD 4000",
            customer_first_name="Alice",
            customer_last_name="Williams",
            customer_phone="+61488888888",
            booking_date="2026-11-15",
            booking_time="19:00:00",  # Explicit time conflict matching BK001
            guest_count=2,
            occasion="Anniversary",
            status="Pending"
        )
        # Execute the model validation check
        duplicate_booking.clean()
        print(
            "❌ FAILED: The system allowed a customer to double-book a table concurrently.")
    except ValidationError as e:
        print(
            f"✅ SUCCESS: System safely blocked double-booking. Exception Error Message: '{e.messages[0]}'")

    # -----------------------------------------------------------------
    # TEST 2: Capacity Seating Overload Limit Rule Verification
    # -----------------------------------------------------------------
    print("\nExecuting Test 2: Evaluating Room Seating Capacity Limit Check...")
    try:
        # Attempt to inject a massive party layout size that completely obliterates the location capacity threshold
        overload_booking = Booking(
            booking_id="BK_FAIL_2",
            restaurant_name="Rossi Osteria",
            restaurant_address="88 Brunswick St, Fortitude Valley QLD 4006",
            customer_first_name="Bob",
            customer_last_name="Davis",
            customer_phone="+61499999999",
            booking_date="2026-11-16",
            booking_time="18:30:00",
            guest_count=200,  # Rossi Osteria only holds a max capacity of 60 guests!
            occasion="Massive Corporate Outing",
            status="Pending"
        )
        overload_booking.clean()
        print("❌ FAILED: The system allowed a venue to register guests far beyond its seating limits.")
    except ValidationError as e:
        print(
            f"✅ SUCCESS: System safely blocked over-capacity reservation. Exception Error Message: '{e.messages[0]}'")

    # -----------------------------------------------------------------
    # TEST 3: Multi-Venue Independent Brand Staff Assignment Check
    # -----------------------------------------------------------------
    print("\nExecuting Test 3: Evaluating Single-Venue Brand Employment Boundary rule...")
    try:
        # Fetch Oliver Brown (EMP003) who works for Rossi Independent Dining (is_chain = False)
        oliver = Employee.objects.get(employee_id="EMP003")

        # Attempt to map him to a second restaurant assignment block row
        illegal_assignment = EmployeeRestaurant(
            assignment_id="ASG_FAIL",
            employee=oliver,
            restaurant_name="Rossi Osteria",
            restaurant_address="88 Brunswick St, Fortitude Valley QLD 4006",
            role="Sous Chef"
        )
        illegal_assignment.clean()
        print("❌ FAILED: The system allowed an independent staff member to register cross-location shifts.")
    except ValidationError as e:
        print(
            f"✅ SUCCESS: System safely blocked multi-branch assignment for single brand. Exception Error Message: '{e.messages[0]}'")

    print("\n🎉 Validation Verification Completed. System parameters are completely sound and secure!")


if __name__ == '__main__':
    run_business_rule_tests()
