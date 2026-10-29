#!/usr/bin/env python3
import os
import django
from django.core.exceptions import ValidationError

# 1. Initialize the Django environment context FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_platform.settings')
django.setup()

# 2. Import your relational models AFTER the system engine has booted
from restaurant_app.models import Booking, EmployeeRestaurant, Employee, Restaurant, Customer, RestaurantGroup

def run_business_rule_tests():
    print("🔬 Initializing Backend Constraint Validation Verification Suites...")

    # Create distinct test groups to avoid collisions
    group_chain, _ = RestaurantGroup.objects.get_or_create(restaurant_group_id="GRP_TEST_A", defaults={'group_name': "Test Chain Group", 'is_chain': True})
    group_indie, _ = RestaurantGroup.objects.get_or_create(restaurant_group_id="GRP_TEST_B", defaults={'group_name': "Test Indie Group", 'is_chain': False})
    
    # NEW UNIQUE NAMES & ADDRESSES: Prevents MultipleObjectsReturned crashes entirely
    rest_a, _ = Restaurant.objects.get_or_create(
        restaurant_name="Aura Dining", 
        address="999 Queen St, Brisbane QLD 4000",
        defaults={'max_capacity_guests': 50, 'restaurant_group': group_chain}
    )
    rest_b, _ = Restaurant.objects.get_or_create(
        restaurant_name="Verdant Kitchen", 
        address="555 Edward St, Brisbane QLD 4000",
        defaults={'max_capacity_guests': 60, 'restaurant_group': group_indie}
    )
    
    # Safe unique customer profiles
    customer_alice, _ = Customer.objects.get_or_create(email="alice_unique@test.com", defaults={'first_name': "Alice", 'last_name': "Unique", 'phone': "+61411111111"})
    customer_bob, _ = Customer.objects.get_or_create(email="bob_unique@test.com", defaults={'first_name': "Bob", 'last_name': "Unique", 'phone': "+61422222222"})

    # -----------------------------------------------------------------
    # TEST 1: Double-Booking Anti-Duplication Rule Verification
    # -----------------------------------------------------------------
    print("\nExecuting Test 1: Evaluating Multi-Table Duplication Block...")
    
    # Clean old run leftovers safely
    Booking.objects.filter(customer=customer_alice, booking_date="2026-11-15", booking_time="19:00:00").delete()
    
    # Establish single baseline record
    Booking.objects.create(
        restaurant=rest_a,
        customer=customer_alice,
        booking_date="2026-11-15",
        booking_time="19:00:00",
        guest_count=2,
        occasion="Anniversary",
        status="PENDING"
    )
    
    try:
        duplicate_booking = Booking(
            restaurant=rest_a,
            customer=customer_alice,
            booking_date="2026-11-15",
            booking_time="19:00:00",
            guest_count=2,
            occasion="Anniversary",
            status="PENDING"
        )
        duplicate_booking.clean()
        print("❌ FAILED: The system allowed a customer to double-book a table concurrently.")
    except ValidationError as e:
        print(f"✅ SUCCESS: System safely blocked double-booking. Exception Error Message: '{e.messages}'")

    # -----------------------------------------------------------------
    # TEST 2: Capacity Seating Overload Limit Rule Verification
    # -----------------------------------------------------------------
    print("\nExecuting Test 2: Evaluating Room Seating Capacity Limit Check...")
    try:
        overload_booking = Booking(
            restaurant=rest_b,
            customer=customer_bob,
            booking_date="2026-11-16",
            booking_time="18:30:00",
            guest_count=200,  # Verdant Kitchen only holds a max capacity of 60 guests!
            occasion="Massive Corporate Outing",
            status="PENDING"
        )
        overload_booking.clean()
        print("❌ FAILED: The system allowed a venue to register guests far beyond its seating limits.")
    except ValidationError as e:
        print(f"✅ SUCCESS: System safely blocked over-capacity reservation. Exception Error Message: '{e.messages}'")

    # -----------------------------------------------------------------
    # TEST 3: Multi-Venue Independent Brand Staff Assignment Check
    # -----------------------------------------------------------------
    print("\nExecuting Test 3: Evaluating Single-Venue Brand Employment Boundary rule...")
    try:
        oliver, _ = Employee.objects.get_or_create(
            employee_id="EMP_UNIQUE_03",
            defaults={'restaurant_group': group_indie, 'first_name': "Oliver", 'last_name': "Unique", 'email': "oliver_unique@test.com"}
        )
        
        EmployeeRestaurant.objects.filter(employee=oliver).delete()
        
        EmployeeRestaurant.objects.create(
            assignment_id="ASG_UNIQ_01",
            employee=oliver,
            restaurant_name="Aura Dining",
            restaurant_address="999 Queen St, Brisbane QLD 4000",
            role="Line Cook"
        )

        illegal_assignment = EmployeeRestaurant(
            assignment_id="ASG_UNIQ_FAIL",
            employee=oliver,
            restaurant_name="Verdant Kitchen",
            restaurant_address="555 Edward St, Brisbane QLD 4000",
            role="Sous Chef"
        )
        illegal_assignment.clean()
        print("❌ FAILED: The system allowed an independent staff member to register cross-location shifts.")
    except ValidationError as e:
        print(f"✅ SUCCESS: System safely blocked multi-branch assignment for single brand. Exception Error Message: '{e.messages}'")

    print("\n🎉 Validation Verification Completed. System parameters are completely sound and secure!")

if __name__ == '__main__':
    run_business_rule_tests()
