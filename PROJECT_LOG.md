# Project Log: Restaurant Booking Platform (CS 360)

Stack:         Django, PostgreSQL, VS Code, Git
Scope:         Phase 1 MVP
Last updated:  Oct 30, 2026
Dates:         From file times and work sessions


---


## COMPLETED


### Oct 22
  - Django project and app setup
  - PostgreSQL configured
  - ER diagram and schema design
  - Sample CSV data created
  - Initial migration and Git repo


### Oct 27
  - Permissions (header-based)
  - API views and URL routing


### Oct 29
  - Repo cleanup and .gitignore

  - Models updated
      - consent, hours, staff notes
      - real ForeignKeys

  - Migration 0002 applied
  - Admin site rewritten
  - Seed script rewritten, data reloaded
  - Settings: time zone, email, login URLs
  - Admin login created and verified


### Oct 30
  - Project log created and committed

  - Guest site built and committed
      - home page
      - booking form
      - confirmation page
      - commit f5fd38e

  - Confirmation email added
      - console backend

  - Dev server runs, system check clean


---


## PENDING


### Testing
  - Test booking form end to end
      - booking appears in admin
      - email prints in terminal

  - Test form rules
      - closed hours
      - duplicate booking
      - past date

  - Cross-browser and device testing
  - Update test_constraints.py


### Setup and cleanup
  - Add rest_framework to INSTALLED_APPS
  - Set different hours per location
  - Check seed.py change (shows as modified)
  - Fix BookingViewSet guest permissions


### New features
  - Staff login (real sessions)
  - Staff booking dashboard
  - Cancellation and modification emails
  - Reminder emails
  - Guest "manage my booking" page
  - Reporting page


---


## PROPOSAL DELIVERABLES


  1. Guest booking
       Built Oct 30, needs testing

  2. Staff dashboard
       Pending

  3. Customer/CRM
       In progress (model done)

  4. Email
       In progress (confirmation built)

  5. Two locations
       In progress (hours pending)

  6. Roles/permissions
       In progress (needs login)

  7. Reporting
       Pending

  8. Synthetic data
       Complete (Oct 29)


---


## ISSUES AND FIXES


### Oct 29

  - .DS_Store still untracked
      Fix: .gitignore had stray spaces;
           rewrote it

  - cat -A failed on macOS
      Fix: used cat -et

  - Time zone typo "Austrailia"
      Fix: corrected to Australia/Brisbane

  - New models.py not applied
      Fix: cleared file, repasted, verified

  - admin.E108 on AllergyAdmin
      Fix: Allergy uses allergy_id;
           rewrote admin.py

  - Seed script broke on new models
      Fix: rewrote to use ForeignKeys

  - git log stuck on (END)
      Fix: pressed q (pager)


### Oct 30

  - Log said guest site was done, but
    the files did not exist
      Found: git status and ls
      Fix: created all files with terminal
           commands, verified with
           git status and manage.py check

  - Log was too wide for VS Code
      Fix: rewrote as short bullet lines


---


## DESIGN DECISIONS

  - Cancelled/no-show bookings don't
    block others

  - Capacity checked per 2-hour window

  - Added consent, hours, staff notes

  - Allergies and staff use real
    ForeignKeys

  - Menu/order/visit models skipped
    (out of scope)

  - Email uses console backend
    (no real emails)

  - Customer + Booking saved in one
    transaction

  - Returning guests keep stored name;
    consent can only be opted in

  - Confirmation page opens only in the
    browser that made the booking

  - 5 restaurants loaded; demo with 2


---


## LOCAL URLS

Start:  python3 manage.py runserver
Stop:   Ctrl+C
Note:   Works only while running,
        on this computer.


  - Home
      http://127.0.0.1:8000/
      Built Oct 30, needs testing

  - Booking form
      http://127.0.0.1:8000/book/
      Built Oct 30, needs testing

  - Confirmation
      http://127.0.0.1:8000/book/confirmed/ID/
      Built Oct 30, needs testing

  - Admin
      http://127.0.0.1:8000/admin/
      Working Oct 29

  - API
      http://127.0.0.1:8000/api/
      Needs rest_framework installed

  - Staff login
      /login/
      Pending

  - Staff dashboard
      /dashboard/
      Pending

  - Reports
      Not assigned
      Pending


---


## NEXT STEPS

  1. Test booking form end to end
  2. Add rest_framework to INSTALLED_APPS
  3. Set different hours for two locations
  4. Build staff login and dashboard
  5. Add cancellation and modification emails
  6. Build reporting page
  7. Update test_constraints.py