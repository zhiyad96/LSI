# 🧪 LSI - Laboratory Information System

LSI (Laboratory Information System) is a full-featured healthcare laboratory management platform built using Django and Django REST Framework. The system manages patients, laboratory orders, sample collection, test processing, result entry, and report generation using role-based access control.

---

 Features

 Authentication & Authorization
- JWT Authentication
- Role-Based Access Control (RBAC)
- Multiple User Roles:
  - Admin
  - Physician
  - Nurse
  - Phlebotomist
  - Lab Technician

username : "ziyad"
admin login passsword : admin1234

---
 Modules

 Patient Management
- Register patients
- Update patient records
- View patient history

 Test Management
- Test Menu Master
- Assay Master
- Laboratory test configuration

 Order Management
- Create laboratory orders
- Assign assays/tests
- Track order status

Phlebotomist Module
- View collection worklist
- Collect samples
- Mark samples as collected

 Lab Technician Module
- Receive samples in lab
- Mark orders as In-Lab
- Enter test results
- Complete laboratory orders
- Generate reports

 Physician Module
- View patient laboratory orders
- Track reports
- Access completed results

 Nurse Module
- Create orders for patients
- View reports
- Search patients and assays

---

 Tech Stack

## Backend
- Python
- Django
- Django REST Framework
- JWT Authentication

## Frontend
- HTML
- Bootstrap 5
- JavaScript

## Database
- SQLite (Development)
- PostgreSQL (Production Ready)

---

 Project Structure

```bash
LSI/
│
├── accounts/
├── admin/
├── nurse/
├── physician/
├── phlebotomist/
├── templates/
├── manage.py
└── requirements.txt
