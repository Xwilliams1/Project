# 📊 Restaurant SaaS Platform - Database Schema Matrix

This flowchart maps out the relational database tables live inside your **PostgreSQL Cluster**, tracking core business operations, user roles, security rules, and customer CRM notes.

### 📐 Visual Entity-Relationship Diagram

```mermaid
%%{init: {
  "theme": "default",
  "themeVariables": {
    "fontSize": "26px",
    "fontFamily": "sans-serif",
    "lineColor": "#51ff00",
    "connectionColor": "#ff0000"
  }
}}%%
erDiagram
    SUPERADMIN {
        string superadmin_id PK
        string first_name
        string last_name
        string email
        string phone
        text address
        date dob
    }

    RESTAURANT_GROUP {
        string restaurant_group_id PK
        string group_name
        boolean is_chain
    }

    OWNER {
        string owner_id PK
        string restaurant_id FK
        string first_name
        string last_name
        string email
        string phone
        text address
        date dob
        boolean is_locked_out
    }

    RESTAURANT {
        int id PK
        string restaurant_group_id FK
        string restaurant_name
        text address
        string phone
        int max_capacity_guests
    }

    EMPLOYEE {
        string employee_id PK
        string restaurant_group_id FK
        string first_name
        string last_name
        string email
        string phone
        text address
        date dob
        decimal base_annual_salary
        boolean is_locked_out
    }

    EMPLOYEE_RESTAURANT {
        string assignment_id PK
        string employee_id FK
        string restaurant_name
        text address
        string role
    }

    CUSTOMER {
        int id PK
        string first_name
        string last_name
        string email UK
        string phone
        text address
        date dob
        date anniversary_date
        text important_occasion_notes
    }

    ALLERGY {
        string allergy_id PK
        string customer_id FK
        string allergy_name
        string severity_level
        text staff_notes
    }

    BOOKING {
        int id PK
        int restaurant_id FK
        int customer_id FK
        date booking_date
        time booking_time
        int guest_count
        string occasion
        string status
        text customer_notes
    }

    RESTAURANT_GROUP ||--o{ OWNER : "owns"
    RESTAURANT_GROUP ||--o{ RESTAURANT : "manages"
    RESTAURANT_GROUP ||--o{ EMPLOYEE : "employs"
    EMPLOYEE ||--o{ EMPLOYEE_RESTAURANT : "assigned_to"
    RESTAURANT ||--o{ BOOKING : "hosts"
    CUSTOMER ||--o{ BOOKING : "reserves"
    CUSTOMER ||--o{ ALLERGY : "tracks_health"
```
