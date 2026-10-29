# Project Log: Restaurant Booking Platform (CS 360)

Stack: Django, PostgreSQL, VS Code, Git
Scope: Phase 1 MVP
Last updated: Oct 30, 2026
Dates are from file times and work sessions.

---

## Completed

- Oct 22 - Django project and app setup
- Oct 22 - PostgreSQL configured
- Oct 22 - ER diagram and schema design
- Oct 22 - Sample CSV data created
- Oct 22 - Initial migration and Git repo
- Oct 27 - Permissions (header-based)
- Oct 27 - API views and URL routing
- Oct 29 - Repo cleanup and .gitignore
- Oct 29 - Models updated (consent, hours, staff notes, ForeignKeys)
- Oct 29 - Migration 0002 applied
- Oct 29 - Admin site rewritten
- Oct 29 - Seed script rewritten, data reloaded
- Oct 29 - Settings: time zone, email, login URLs
- Oct 29 - Admin login created and verified
- Oct 30 - Guest site: home, booking form, confirmation page
- Oct 30 - Confirmation email (console backend)

## Pending

- Add rest_framework to INSTALLED_APPS
- Set different hours per location
- Test booking form end to end
- Staff login (real sessions)
- Staff booking dashboard
- Reminder and cancellation emails
- Guest "manage my booking" page
- Reporting page
- Fix BookingViewSet guest permissions
- Update test_constraints.py
- Cross-browser and device testing

---

## Proposal Deliverables

1. Guest booking     - Built, needs testing
2. Staff dashboard   - Pending
3. Customer/CRM      - In progress (model done)
4. Email             - In progress (confirmation done)
5. Two locations     - In progress (hours pending)
6. Roles/permissions - In progress (needs login)
7. Reporting         - Pending
8. Synthetic data    - Complete (Oct 29)

---

## Issues and Fixes (all Oct 29)

- .DS_Store still untracked
  Fix: .gitignore had stray spaces; rewrote it
- cat -A failed on macOS
  Fix: used cat -et
- Time zone typo "Austrailia"
  Fix: corrected to Australia/Brisbane
- New models.py not applied
  Fix: cleared file, repasted, verified
- admin.E108 on AllergyAdmin
  Fix: Allergy uses allergy_id; rewrote admin.py
- Seed script broke on new models
  Fix: rewrote to use ForeignKeys
- git log stuck on (END)
  Fix: pressed q (pager)

---

## Design Decisions

- Cancelled/no-show bookings don't block others
- Capacity checked per 2-hour window
- Added consent, hours, staff notes
- Allergies and staff use real ForeignKeys
- Menu/order/visit models skipped (out of scope)
- Email uses console backend (no real emails)
- Customer + Booking saved in one transaction
- 5 restaurants loaded; demo with 2

---

## Local URLs

Start: python3 manage.py runserver
Stop: Ctrl+C
Works only while running, on this computer.

- Home: http://127.0.0.1:8000/
  Built Oct 30
- Booking form: http://127.0.0.1:8000/book/
  Built Oct 30
- Confirmation: http://127.0.0.1:8000/book/confirmed/ID/
  Built Oct 30
- Admin: http://127.0.0.1:8000/admin/
  Working Oct 29
- API: http://127.0.0.1:8000/api/
  Needs rest_framework installed
- Staff login: /login/ - Pending
- Staff dashboard: /dashboard/ - Pending
- Reports: not assigned - Pending

---

## Next Steps

1. Test booking form end to end
2. Add rest_framework to INSTALLED_APPS
3. Set different hours for two locations
4. Build staff login and dashboard
5. Add cancellation and reminder emails
6. Build reporting page
7. Update test_constraints.py