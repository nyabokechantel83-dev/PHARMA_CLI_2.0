# Pharma-CLI
#  Pharma-CLI

**Pharma-CLI** is a Python-based command-line pharmacy management system that allows customers, doctors, and pharmacists to interact with a pharmacy through a terminal interface.

The application demonstrates **Object-Oriented Programming (OOP)**, role-based access control, authentication, prescription management, drug inventory, order processing, prescription verification, persistent data storage, and automated testing.





##  Project Overview

Pharma-CLI provides a simple command-line environment for managing pharmaceutical operations.

The system supports three main user roles:

*  **Customer**
*  **Doctor**
*  **Pharmacist**

Each role has different permissions and responsibilities within the system.

The application starts from `main.py`, which handles command-line arguments and connects users to the appropriate customer, doctor, pharmacist, and authentication functionality.

---

##  Features

###  Authentication & User Management

Users can:

* Register an account
* Log in
* Log out
* Check the currently logged-in user
* Select a user role during registration
* Authenticate using a password

Passwords are securely hashed using **Argon2**.

Example registration:

```bash
python main.py register --name "John Doe" --email "john@example.com" --password "password123" --role customer
```

Example login:

```bash
python main.py login --email "john@example.com" --password "password123"
```

Check the currently logged-in user:

```bash
python main.py whoami
```

Log out:

```bash
python main.py logout
```

---

#  User Roles

##  Customer

Customers can interact with the pharmacy by:

* Viewing available drugs
* Ordering medication
* Purchasing over-the-counter medication
* Providing prescription references when required
* Viewing and managing their orders

Prescription-only medication requires a valid prescription before an order can be processed.



##  Doctor

Doctors are responsible for prescription management.

They can:

* View available functionality
* Issue prescriptions
* Associate prescriptions with customers
* Specify medication and dosage information
* Create prescription references

Prescriptions can then be used by customers when purchasing prescription-only medication.



##  Pharmacist

Pharmacists manage the pharmacy side of the system.

They can:

* Manage drug inventory
* Add drugs
* View available drugs
* Manage stock
* View customer orders
* Claim orders
* Verify prescriptions
* Approve or reject orders



# Prescription Verification

Pharma-CLI separates **over-the-counter (OTC)** medication from **prescription-only medication**.

When a customer attempts to order a prescription drug, the system verifies the prescription reference.

The verification process checks whether:

1. The prescription exists.
2. The prescription has expired.
3. The prescription has already been used.
4. The prescription is valid.

Possible verification results include:


not_found
expired
already_used
verified


### Prescription Order Flow


Customer
   │
   ▼
Select Drug
   │
   ▼
Prescription Required?
   │
   ├── No ───────────────► Create OTC Order
   │
   ▼
Provide Prescription Reference
   │
   ▼
Verify Prescription
   │
   ├── Not Found ────────► Reject
   │
   ├── Expired ──────────► Reject
   │
   ├── Already Used ─────► Reject
   │
   └── Verified ─────────► Create Order
                                │
                                ▼
                         Pharmacist Review
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                      Approve        Reject




#  Order Management

The order system supports both OTC and prescription medication.

### OTC Order


Customer
    ↓
Select OTC Drug
    ↓
Check Stock
    ↓
Create Order
    ↓
Pharmacist Reviews
    ↓
Approve / Reject


### Prescription Order


Customer
    ↓
Select Prescription Drug
    ↓
Enter Prescription Reference
    ↓
Prescription Verification
    ↓
Create Pending Order
    ↓
Pharmacist Reviews
    ↓
Approve / Reject




#  OTC Advisory

The system includes an OTC advisory feature to provide basic guidance when customers request over-the-counter medication.

This functionality is intended to support the ordering process while keeping prescription-only medication subject to prescription verification.



#  Data Persistence

Pharma-CLI uses local data storage to maintain application information between sessions.

The project includes a dedicated:


data/


directory.

Storage-related functionality is handled through the utility layer, including `utils/storage.py`.

This allows application data such as users, drugs, prescriptions, and orders to be stored and retrieved without requiring an external database.


#  Project Architecture

The project is organized into separate layers to keep responsibilities clear.


Pharma-CLI/
│
├── cli/
│   ├── customer.py
│   ├── doctor.py
│   ├── menu.py
│   ├── pharmacist.py
│   └── user.py
│
├── models/
│   ├── user.py
│   ├── drug.py
│   ├── prescription.py
│   └── order.py
│
├── utils/
│   ├── auth.py
│   ├── storage.py
│   └── verify.py
│
├── data/
│
├── tests/
│   ├── test_auth.py
│   ├── test_doctor.py
│   ├── test_drug.py
│   ├── test_menu.py
│   ├── test_models.py
│   ├── test_order.py
│   ├── test_pharmacist.py
│   ├── test_prescription.py
│   └── test_verify.py
│
├── main.py
├── requirements.txt
├── Pipfile
├── Pipfile.lock
└── README.md


The repository currently follows this modular structure across its CLI, model, utility, data, and test components.



#  Models

The `models/` package contains the core objects used by the application:

### `User`

Represents users registered in the pharmacy system and their assigned roles.

### `Drug`

Represents medication available in the pharmacy, including information such as price, stock, and prescription requirements.

### `Prescription`

Represents prescriptions issued by doctors and used when ordering prescription-only medication.

### `Order`

Represents customer medication orders and their processing status.

The current repository contains these four model modules.



#  Command-Line Interface

The application can be used either through the interactive menu or through command-line commands.

Running:

```bash
python main.py
```

starts the interactive menu.

The application also supports command-based interaction.

### Available account commands

```bash
python main.py register
python main.py login
python main.py logout
python main.py whoami
```

The CLI also registers commands for:

```text
Customer
Doctor
Pharmacist
```

These commands are connected to their respective modules from `main.py`.

---

#  Technologies Used

| Technology            | Purpose                           |
| --------------------- | --------------------------------- |
| **Python 3**          | Main programming language         |
| **OOP**               | Application architecture          |
| **Argparse**          | Command-line interface            |
| **JSON/File Storage** | Persistent application data       |
| **Argon2**            | Password hashing                  |
| **Pytest**            | Automated testing                 |
| **Pipenv**            | Dependency/environment management |
| **Git & GitHub**      | Version control and collaboration |

The project's dependency configuration includes Argon2 and Pytest, with `pytest==9.1.1` and `pytest-cov==7.1.0` currently specified in `requirements.txt`.



#  Installation

## 1. Clone the repository

```bash
git clone https://github.com/josephinenjuguna-ship-it/Pharma-CLI.git
```

Move into the project directory:

```bash
cd Pharma-CLI
```


## 2. Create a virtual environment

### Using Python

```bash
python -m venv venv
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The repository also includes a `Pipfile` and `Pipfile.lock` for Pipenv-based environment management.

---

#  Running the Application

Start Pharma-CLI with:

```bash
python main.py
```

You should see the interactive application menu.

You can also use the CLI directly.

For example:

```bash
python main.py --version
```

Expected output:

```text
pharma-cli 0.1.0
```



#  Testing

Pharma-CLI uses **Pytest** for automated testing.

Run the complete test suite:

```bash
pytest
```

Run a specific test module:

```bash
pytest tests/test_order.py
```

For prescription verification:

```bash
pytest tests/test_verify.py
```

For authentication:

```bash
pytest tests/test_auth.py
```

The repository currently contains tests covering authentication, doctors, drugs, menus, models, orders, pharmacists, prescriptions, and verification.



#  Testing Areas

| Test File              | Area                      |
| ---------------------- | ------------------------- |
| `test_auth.py`         | Authentication            |
| `test_doctor.py`       | Doctor functionality      |
| `test_drug.py`         | Drug functionality        |
| `test_menu.py`         | CLI menu                  |
| `test_models.py`       | Core models               |
| `test_order.py`        | Orders                    |
| `test_pharmacist.py`   | Pharmacist functionality  |
| `test_prescription.py` | Prescriptions             |
| `test_verify.py`       | Prescription verification |



#  Security

The application uses **Argon2** for password hashing rather than storing passwords as plain text.

Authentication functionality is separated into:


utils/auth.py


while the user model is maintained separately under:

models/user.py


This separation helps keep authentication logic independent from the rest of the application.



# Application Flow


                         ┌──────────────────┐
                         │    START APP     │
                         │     main.py      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ REGISTER / LOGIN │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  AUTHENTICATION  │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        ┌───────────┐       ┌───────────┐       ┌────────────┐
        │ CUSTOMER  │       │  DOCTOR   │       │ PHARMACIST │
        └─────┬─────┘       └─────┬─────┘       └──────┬─────┘
              │                   │                    │
              ▼                   ▼                    ▼
        Browse Drugs        Issue Prescription    Manage Drugs
              │                   │               Manage Orders
              ▼                   │                    │
        Create Order              │                    │
              │                   │                    │
              └───────────────────┼────────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ ORDER PROCESSING │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ VERIFY / REVIEW  │
                         └────────┬─────────┘
                                  │
                          ┌───────┴───────┐
                          ▼               ▼
                      APPROVED          REJECTED




#  Git Workflow

The project is developed collaboratively using Git and GitHub.

The repository's current default branch is:


feature-development


Feature development is separated into branches so that individual functionality can be developed and tested before integration.

Examples include:


feature-development
feature/rbac-auth
feature/drug-inventory-logic
feature/doctor-issue-prescription
feature/order-claim-logic
feature/otc-advisory-logic


This workflow allows the team to work on separate features while reducing conflicts during integration.



#  Project Objectives

The main objectives of Pharma-CLI are to demonstrate practical application of:

* Object-Oriented Programming
* Python development
* Command-line application design
* Authentication
* Role-Based Access Control
* Data persistence
* Error handling
* Prescription verification
* Inventory management
* Order management
* Automated testing
* Git and GitHub collaboration
* Team-based software development



#  Future Improvements

Potential future improvements include:

*  Migration from JSON storage to SQLite/PostgreSQL
*  Web-based interface
*  Mobile application
*  Payment integration
*  Email notifications
*  Pharmacy analytics and reporting
*  Advanced drug search
*  Improved inventory management
*  More detailed user dashboards
*  Additional security controls
*  Deployment as a production web application



#  Team

Pharma-CLI was developed as a collaborative software engineering project.

### Contributors

* **Josephine Njuguna** — Scrum Master / Order & Verification functionality
* **Weru Dennis** — Authentication & RBAC
* **Chantel Nyaboke** — Drug Inventory
* **John Macharia** — Prescription Management



# Educational Purpose

Pharma-CLI was developed as a software engineering project to demonstrate the practical application of Python, Object-Oriented Programming, testing, version control, and collaborative development.



##  License

This project is currently intended for **educational purposes**.



##  Repository

**GitHub:**
https://github.com/josephinenjuguna-ship-it/Pharma-CLI

