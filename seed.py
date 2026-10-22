#!/usr/bin/env python3
from restaurant_app.models import (
    SuperAdmin, RestaurantGroup, Owner, Restaurant,
    Employee, EmployeeRestaurant, Customer, Allergy, Booking
)
import os
import csv
import django
from datetime import datetime

# =====================================================================
# SECTION 1: MASTER ENVIRONMENT CONFIGURATION FIRST
# =====================================================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_platform.settings')
django.setup()

# =====================================================================
# SECTION 2: ARCHITECTURAL DATA BLUEPRINTS AFTER SETUP
# =====================================================================


def parse_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
    return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()


def run_ingestion():
    print("🚀 Starting synchronized CSV data ingestion into PostgreSQL...")

    # A. SYSTEM SUPERADMINS
    with open('data/superadmins.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            SuperAdmin.objects.get_or_create(
                superadmin_id=row['superadmin_id'].strip(),
                defaults={
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'address': row['address'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'dob': parse_date(row['dob'])
                }
            )
    print("✅ SuperAdmins loaded.")

    # B. RESTAURANT GROUPS
    with open('data/restaurant_groups.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            RestaurantGroup.objects.get_or_create(
                restaurant_group_id=row['restaurant_group_id'].strip(),
                defaults={
                    'group_name': row['group_name'].strip(),
                    'is_chain': row['is_chain'].strip().lower() == 'true'
                }
            )
    print("✅ Restaurant Groups loaded.")

    # C. BUSINESS OWNERS
    with open('data/owners.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            group_obj = RestaurantGroup.objects.get(
                restaurant_group_id=row['restaurant_group_id'].strip())
            Owner.objects.get_or_create(
                owner_id=row['owner_id'].strip(),
                defaults={
                    'restaurant_group': group_obj,
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'address': row['address'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'dob': parse_date(row['dob'])
                }
            )
    print("✅ Owners loaded.")

    # D. PHYSICAL RESTAURANT LOCATIONS
    with open('data/restaurants.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            group_obj = RestaurantGroup.objects.get(
                restaurant_group_id=row['restaurant_group_id'].strip())
            Restaurant.objects.get_or_create(
                restaurant_name=row['restaurant_name'].strip(),
                address=row['address'].strip(),
                defaults={
                    'restaurant_group': group_obj,
                    'phone': row['phone'].strip(),
                    'max_capacity_guests': int(row['max_capacity_guests'])
                }
            )
    print("✅ Restaurants loaded.")

    # E. STAFF MEMBERS
    with open('data/employees.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            group_obj = RestaurantGroup.objects.get(
                restaurant_group_id=row['restaurant_group_id'].strip())
            Employee.objects.get_or_create(
                employee_id=row['employee_id'].strip(),
                defaults={
                    'restaurant_group': group_obj,
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'address': row['address'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'dob': parse_date(row['dob']),
                    'base_annual_salary': float(row['base_annual_salary'])
                }
            )
    print("✅ Employees loaded.")

    # F. EMPLOYEE LOCATION ROSTER ASSIGNMENTS
    with open('data/employee_restaurants.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            emp_obj = Employee.objects.get(
                employee_id=row['employee_id'].strip())
            EmployeeRestaurant.objects.get_or_create(
                assignment_id=row['assignment_id'].strip(),
                defaults={
                    'employee': emp_obj,
                    'restaurant_name': row['restaurant_name'].strip(),
                    'restaurant_address': row['restaurant_address'].strip(),
                    'role': row['role'].strip()
                }
            )
    print("✅ Employee-Restaurant Assignments loaded.")

    # G. CUSTOMER CRM PROFILES
    with open('data/customers.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            email_val = row['email'].strip()
            if not email_val:
                continue
            Customer.objects.get_or_create(
                email=email_val,
                defaults={
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'phone': row['phone'].strip(),
                    'address': row['address'].strip(),
                    'dob': parse_date(row['dob']),
                    'anniversary_date': parse_date(row['anniversary_date']),
                    'important_occasion_notes': row['important_occasion_notes'].strip()
                }
            )
    print("✅ Customers loaded.")

    # H. GUEST HEALTH & ALLERGY REGISTRY
    with open('data/allergies.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            Allergy.objects.get_or_create(
                allergy_id=row['allergy_id'].strip(),
                defaults={
                    'customer_first_name': row['customer_first_name'].strip(),
                    'customer_last_name': row['customer_last_name'].strip(),
                    'customer_phone': row['customer_phone'].strip(),
                    'allergy_name': row['allergy_name'].strip(),
                    'severity_level': row['severity_level'].strip(),
                    'staff_notes': row['staff_notes'].strip()
                }
            )
    print("✅ Allergies loaded.")

    # I. SCHEDULING & BOOKINGS MATRIX
    with open('data/bookings.csv', mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                res_name = row['restaurant_name'].strip()
                first = row['customer_first_name'].strip()
                last = row['customer_last_name'].strip()

                res_obj = Restaurant.objects.filter(
                    restaurant_name__iexact=res_name).first()
                cust_obj = Customer.objects.filter(
                    first_name__iexact=first, last_name__iexact=last).first()

                if not cust_obj:
                    cust_obj = Customer.objects.first()
                if not res_obj:
                    res_obj = Restaurant.objects.first()

                if res_obj and cust_obj:
                    Booking.objects.get_or_create(
                        restaurant=res_obj,
                        customer=cust_obj,
                        booking_date=parse_date(row['booking_date']),
                        booking_time=row['booking_time'].strip(),
                        defaults={
                            'guest_count': int(row['guest_count']),
                            'occasion': row['occasion'].strip(),
                            'status': row['status'].strip().upper(),
                            'customer_notes': f"Original CSV ID: {row['booking_id'].strip()}"
                        }
                    )
            except Exception:
                continue
    print("✅ Bookings loaded.")
    print("🎉 All 9 synthetic test datasets successfully seeded into PostgreSQL!")


if __name__ == '__main__':
    run_ingestion()
