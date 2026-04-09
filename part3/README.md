# 🏠 HBnB — Part 3: SQL Persistence, Authentication & RBAC

---

## Table of Contents

1. [Description](#-description)
2. [Architecture](#-architecture)
3. [Database Schema](#️-database-schema)
4. [Security](#-security)
5. [Project Structure](#-project-structure)
6. [Installation & Usage](#️-installation--usage)
7. [Testing](#-testing)
8. [API Endpoints](#-api-endpoints)
9. [Tech Stack](#️-tech-stack)
10. [Contributors](#-contributors)
11. [License](#-license)

---

## 📋 Description

**HBnB** is a simplified Airbnb-like application built with Flask and Flask-RESTx.

**Part 3** implements a fully persistent REST API backed by a **SQLite relational database** through SQLAlchemy ORM. It features **secure password hashing** with bcrypt and **protected endpoints** using JWT (JSON Web Tokens) with **role-based access control** (RBAC).

> 💡 Thanks to the **Repository Pattern** and the **Facade Pattern**, swapping the data layer only required changing the repository implementation — endpoints and business logic remain untouched.

---

## 🧩 Architecture

The project follows a **three-layer architecture**:

```
Presentation Layer (API / Flask-RESTx)
        ↓
Business Logic Layer (Facade + Models)
        ↓
Persistence Layer (SQLAlchemyRepository → SQLite)
```

**Design patterns used:**
- **Application Factory** — `create_app()` to manage different configs (dev, test)
- **Repository Pattern** — abstract interface with 6 methods, implemented by `SQLAlchemyRepository`
- **Facade Pattern** — single entry point for all business logic

---

## 🗄️ Database Schema

The database contains **5 tables**:

```
users          ──< places
  │                  │
  │                  ├──< reviews
  │                  │
  └──────────────────┘
                     │
              place_amenity >── amenities
```

- **users** — id, first_name, last_name, email (unique), password (bcrypt hash), is_admin
- **places** — id, title, description, price, latitude, longitude, owner_id (FK → users)
- **reviews** — id, text, rating (1–5), user_id (FK → users), place_id (FK → places), UNIQUE(user_id, place_id)
- **amenities** — id, name (unique)
- **place_amenity** — many-to-many association table (place_id, amenity_id)

All entities inherit from a `BaseModel` that provides `id` (UUID), `created_at`, and `updated_at` columns. The `__abstract__ = True` flag prevents SQLAlchemy from creating a useless base table.

---

## 🔐 Security

### Password Hashing (bcrypt)

Passwords are never stored in plain text. They are transformed into an irreversible hash using `bcrypt`:
- **Intentionally slow** — makes brute force attacks expensive
- **Random salt** — identical passwords produce different hashes
- The password is **never returned** by the API (excluded from `to_dict()`)

### JWT (JSON Web Tokens)

Authentication is handled via `POST /api/v1/auth/login`, which returns an `access_token`. This token must be sent in the `Authorization: Bearer <token>` header to access protected routes.

### RBAC (Role-Based Access Control)

| Role | Permissions |
|---|---|
| **User** | Can only modify their own resources |
| **Admin** | Can modify all resources + access admin-only endpoints |

The `is_admin` claim is embedded directly in the JWT payload, avoiding an extra DB query on every authorization check.

---

## 📂 Project Structure

```
part3/
├── app/
│   ├── __init__.py              # App factory (db, bcrypt, jwt, create_all)
│   ├── models/
│   │   ├── baseModel.py         # BaseModel (db.Model, id, created_at, updated_at)
│   │   ├── user.py              # User (bcrypt hash/verify, @validates)
│   │   ├── place.py             # Place (FK owner_id, relationship amenities)
│   │   ├── review.py            # Review (FK user_id, place_id)
│   │   └── amenity.py           # Amenity
│   ├── api/v1/
│   │   ├── users.py             # CRUD users + RBAC
│   │   ├── places.py            # CRUD places
│   │   ├── reviews.py           # CRUD reviews + business rules
│   │   ├── amenities.py         # CRUD amenities
│   │   └── auth.py              # POST /login → JWT token
│   ├── services/
│   │   └── facade.py            # HBnBFacade + UserRepository
│   └── persistence/
│       └── repository.py        # SQLAlchemyRepository (6 methods)
├── scripts/
│   ├── create_tables.sql        # Raw SQL schema (5 tables)
│   └── seed.sql                 # Initial data (admin + amenities)
├── tests/
│   ├── test_user.py             # User tests (creation, email, hash, verify)
│   ├── test_place.py            # Place tests (creation, validations)
│   ├── test_review.py           # Review tests (rating, text)
│   └── test_amenity.py          # Amenity tests (name, validations)
├── config.py                    # DevelopmentConfig + TestingConfig
├── run.py                       # Entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Usage

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone <repo_url>
cd part3
pip install -r requirements.txt
```

### Run the server

```bash
python run.py
```

The API is available at `http://127.0.0.1:5000/`. Swagger UI is accessible at the root URL.

> Tables are created automatically on startup thanks to `db.create_all()` inside `create_app()`.

### Bootstrap the first admin

Since creating users requires admin privileges, the first admin must be created manually:

```bash
flask shell
```

```python
from app import db
from app.models.user import User

admin = User(
    first_name='Admin',
    last_name='HBnB',
    email='admin@hbnb.io',
    password='admin1234',
    is_admin=True
)
admin.hash_password('admin1234')
db.session.add(admin)
db.session.commit()
```

---

## 🧪 Testing

Tests use a dedicated `TestingConfig` with a separate SQLite database (`testing.db`) to ensure production data is never affected. Tables are created before each test and dropped after to guarantee test isolation.

```bash
PYTHONPATH=. pytest tests/ -v
```

Expected result: **17 tests passed**.

---

## 📡 API Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | ❌ | Login → returns a JWT |
| `POST` | `/api/v1/users/` | 🔒 Admin | Create a user |
| `GET` | `/api/v1/users/` | ❌ | List all users |
| `GET` | `/api/v1/users/<id>` | ❌ | Get user details |
| `PUT` | `/api/v1/users/<id>` | 🔒 Owner/Admin | Update a user |
| `POST` | `/api/v1/places/` | 🔒 Auth | Create a place |
| `GET` | `/api/v1/places/` | ❌ | List all places |
| `PUT` | `/api/v1/places/<id>` | 🔒 Owner/Admin | Update a place |
| `POST` | `/api/v1/reviews/` | 🔒 Auth | Create a review |
| `GET` | `/api/v1/places/<id>/reviews` | ❌ | Get reviews for a place |
| `POST` | `/api/v1/amenities/` | 🔒 Admin | Create an amenity |
| `GET` | `/api/v1/amenities/` | ❌ | List all amenities |

### Review Business Rules

- A user **cannot** review their own place → `400`
- A user **cannot** review the same place twice → `400`
- Authentication is **required** to post a review → `401` without token

---

## 🛠️ Tech Stack

- **Flask** + **Flask-RESTx** — Web framework + REST API with Swagger
- **SQLAlchemy** — ORM for Python ↔ SQL mapping
- **Flask-Bcrypt** — Secure password hashing
- **Flask-JWT-Extended** — JWT token management
- **SQLite** — Lightweight relational database
- **Pytest** — Unit testing framework

---

## 👥 Contributors

| Name | GitHub |
|---|---|
| **Frances Palmer** | [@FrancesMP](https://github.com/FrancesMP) |
| **Yohhni Marcellus** | [@youri47](https://github.com/youri47) |
| **Sedra Ramarosaona** | [@SedraR78](https://github.com/SedraR78) |

---

## 📄 License

Project made as part of the [Holberton School](https://www.holbertonschool.com/) curriculum.