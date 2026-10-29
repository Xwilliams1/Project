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
# SECTION 1: DJANGO SETUP (must run before importing models)
# =====================================================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_platform.settings')
django.setup()


# =====================================================================
# SECTION 2: HELPERS
# =====================================================================


def parse_date(value):
    """'2026-11-05' -> date object. Empty text -> None."""
    if not value or not value.strip():
        return None
    return datetime.strptime(value.strip(), '%Y-%m-%d').date()


def parse_time(value):
    """Accepts '18:30' or '18:30:00' -> time object. Empty text -> None."""
    if not value or not value.strip():
        return None
    value = value.strip()
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised time format: {value}")


def parse_bool(value):
    """'true', 'yes', '1' -> True. Anything else (including empty) -> False."""
    return (value or '').strip().lower() in ('true', 'yes', '1')


def find_restaurant(name, address=''):
    """Match a restaurant by name (and address if given). Case-insensitive."""
    qs = Restaurant.objects.filter(restaurant_name__iexact=name.strip())
    if address and address.strip():
        narrowed = qs.filter(address__iexact=address.strip())
        if narrowed.exists():
            return narrowed.first()
    return qs.first()


def find_customer(first, last, phone=''):
    """Match a customer by name; use phone to break ties if several match."""
    qs = Customer.objects.filter(first_name__iexact=first.strip(),
                                 last_name__iexact=last.strip())
    if phone and phone.strip() and qs.count() > 1:
        by_phone = qs.filter(phone=phone.strip())
        if by_phone.exists():
            return by_phone.first()
    return qs.first()


# =====================================================================
# SECTION 3: LOAD DATA
# =====================================================================

def run_ingestion():
    print("Starting CSV data ingestion into PostgreSQL...")

    # A. SUPERADMINS (unchanged)
    with open('data/superadmins.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            SuperAdmin.objects.get_or_create(
                superadmin_id=row['superadmin_id'].strip(),
                defaults={
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'address': row['address'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'dob': parse_date(row['dob']),
                })
    print("SuperAdmins loaded.")

    # B. RESTAURANT GROUPS (unchanged)
    with open('data/restaurant_groups.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            RestaurantGroup.objects.get_or_create(
                restaurant_group_id=row['restaurant_group_id'].strip(),
                defaults={
                    'group_name': row['group_name'].strip(),
                    'is_chain': parse_bool(row['is_chain']),
                })
    print("Restaurant groups loaded.")

    # C. OWNERS (unchanged)
    with open('data/owners.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            group = RestaurantGroup.objects.get(
                restaurant_group_id=row['restaurant_group_id'].strip())
            Owner.objects.get_or_create(
                owner_id=row['owner_id'].strip(),
                defaults={
                    'restaurant_group': group,
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'address': row['address'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'dob': parse_date(row['dob']),
                })
    print("Owners loaded.")

    # D. RESTAURANTS
    # CHANGED: opening_time / closing_time are read if the CSV has those
    # columns (format HH:MM). If not, the model defaults (11:00-22:00) apply.
    with open('data/restaurants.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            group = RestaurantGroup.objects.get(
                restaurant_group_id=row['restaurant_group_id'].strip())
            defaults = {
                'restaurant_group': group,
                'phone': row['phone'].strip(),
                'max_capacity_guests': int(row['max_capacity_guests']),
            }
            opening = parse_time(row.get('opening_time', ''))
            closing = parse_time(row.get('closing_time', ''))
            if opening:
                defaults['opening_time'] = opening
            if closing:
                defaults['closing_time'] = closing
            Restaurant.objects.update_or_create(
                restaurant_name=row['restaurant_name'].strip(),
                address=row['address'].strip(),
                defaults=defaults)
    print("Restaurants loaded.")

    # E. EMPLOYEES (unchanged)
    with open('data/employees.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            group = RestaurantGroup.objects.get(
                restaurant_group_id=row['restaurant_group_id'].strip())
            Employee.objects.get_or_create(
                employee_id=row['employee_id'].strip(),
                defaults={
                    'restaurant_group': group,
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'address': row['address'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'dob': parse_date(row['dob']),
                    'base_annual_salary': row['base_annual_salary'].strip(),
                })
    print("Employees loaded.")

    # F. EMPLOYEE <-> RESTAURANT ASSIGNMENTS
    # CHANGED: the CSV's restaurant_name / restaurant_address columns are now
    # used to FIND the Restaurant row, which is stored as a real ForeignKey.
    # update_or_create (not get_or_create) so rows left over from before the
    # migration, which have an empty restaurant link, get repaired.
    skipped = 0
    with open('data/employee_restaurants.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            employee = Employee.objects.get(
                employee_id=row['employee_id'].strip())
            restaurant = find_restaurant(row['restaurant_name'],
                                         row.get('restaurant_address', ''))
            if not restaurant:
                print(f"  Skipped assignment {row['assignment_id']}: "
                      f"restaurant '{row['restaurant_name']}' not found.")
                skipped += 1
                continue
            try:
                EmployeeRestaurant.objects.update_or_create(
                    assignment_id=row['assignment_id'].strip(),
                    defaults={
                        'employee': employee,
                        'restaurant': restaurant,
                        'role': row['role'].strip(),
                    })
            except Exception as e:  # model rules (group match, single-venue)
                print(f"  Skipped assignment {row['assignment_id']}: {e}")
                skipped += 1
    print(f"Assignments loaded ({skipped} skipped).")

    # G. CUSTOMERS
    # CHANGED: marketing_consent read if the CSV has that column;
    # otherwise it stays False (opt-in only).
    with open('data/customers.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            email = row['email'].strip()
            if not email:
                continue
            Customer.objects.update_or_create(
                email=email,
                defaults={
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'phone': row['phone'].strip(),
                    'address': row['address'].strip(),
                    'dob': parse_date(row['dob']),
                    'anniversary_date': parse_date(row['anniversary_date']),
                    'important_occasion_notes': row['important_occasion_notes'].strip(),
                    'marketing_consent': parse_bool(row.get('marketing_consent', '')),
                })
    print("Customers loaded.")

    # H. ALLERGIES
    # CHANGED: the CSV's customer name/phone columns are used to FIND the
    # Customer, which is stored as a real ForeignKey.
    skipped = 0
    with open('data/allergies.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            customer = find_customer(row['customer_first_name'],
                                     row['customer_last_name'],
                                     row.get('customer_phone', ''))
            if not customer:
                print(f"  Skipped allergy {row['allergy_id']}: customer "
                      f"'{row['customer_first_name']} {row['customer_last_name']}' not found.")
                skipped += 1
                continue
            Allergy.objects.update_or_create(
                allergy_id=row['allergy_id'].strip(),
                defaults={
                    'customer': customer,
                    'allergy_name': row['allergy_name'].strip(),
                    'severity_level': row['severity_level'].strip(),
                    'staff_notes': row['staff_notes'].strip(),
                })
    print(f"Allergies loaded ({skipped} skipped).")

    # I. BOOKINGS
    # CHANGED: uses bulk_create, which skips Booking.save() validation.
    # That is deliberate: seed data includes historical bookings
    # (completed, cancelled, no-show), which the new "no past bookings"
    # rule would otherwise reject. Bookings made through the form/admin
    # are still fully validated.
    # CHANGED: no more silent fallback to Customer.objects.first();
    # unmatched rows are skipped and reported.
    to_create, skipped = [], 0
    with open('data/bookings.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                restaurant = find_restaurant(row['restaurant_name'])
                customer = find_customer(row['customer_first_name'],
                                         row['customer_last_name'])
                if not restaurant or not customer:
                    raise ValueError("restaurant or customer not found")

                date = parse_date(row['booking_date'])
                time = parse_time(row['booking_time'])

                already_there = Booking.objects.filter(
                    restaurant=restaurant, customer=customer,
                    booking_date=date, booking_time=time).exists()
                if already_there:
                    continue  # makes re-running the seed safe

                to_create.append(Booking(
                    restaurant=restaurant,
                    customer=customer,
                    booking_date=date,
                    booking_time=time,
                    guest_count=int(row['guest_count'].strip()),
                    occasion=row.get('occasion', '').strip(),
                    status=(row.get('status') or 'CONFIRMED').strip().upper(),
                    customer_notes=row.get('customer_notes', '').strip(),
                ))
            except Exception as e:
                print(f"  Skipped booking row: {e}")
                skipped += 1
    Booking.objects.bulk_create(to_create)
    print(f"Bookings loaded: {len(to_create)} new, {skipped} skipped.")

    print("\nSeeding complete.")


if __name__ == '__main__':
    run_ingestion()
