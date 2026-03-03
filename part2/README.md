# HBnB Part 2 — Business Logic & API Endpoints

> Technical README — Architecture, Implementation & Design Decisions

---

## Table of Contents

1. [Architecture Overview — 3-Layer Design](#1-architecture-overview)
2. [Task 0 — Project Structure Setup](#2-task-0--project-structure-setup)
3. [Task 1 — Business Logic Classes (Models)](#3-task-1--business-logic-classes)
4. [Repository Pattern — Persistence Layer](#4-repository-pattern--persistence-layer)
5. [The Facade Pattern](#5-the-facade-pattern)
6. [API Endpoints](#6-api-endpoints)
7. [flask-restx — Key Contributions](#7-flask-restx--key-contributions)
8. [Task 6 — Tests](#8-task-6--tests)
9. [Running the Application](#9-running-the-application)

---

## 1. Architecture Overview

HBnB Part 2 is built on a strict 3-layer architecture. The core principle: each layer has no knowledge of the internal details of the other layers. They communicate only through defined interfaces.

| Layer | Location | Role |
|---|---|---|
| **Presentation** | `app/api/` | HTTP requests, input validation, JSON responses |
| **Business Logic** | `app/models/` | Entities, validations, business rules, relations |
| **Persistence** | `app/persistence/` | Data storage & retrieval (RAM in Part 2, SQL in Part 3) |
| **Facade** | `app/services/` | Bridge between Presentation and Business Logic |

**Why this separation?** In Part 3, the in-memory storage is replaced by SQL. Because the layers are cleanly separated, only the Facade and the Repository need to change — endpoints and models remain completely untouched.

---

## 2. Task 0 — Project Structure Setup

```
hbnb/
├── run.py                  # Entry point — instantiates the app and starts the server
├── config.py               # Flask config: SECRET_KEY, DEBUG mode
└── app/
    ├── __init__.py         # Factory function create_app()
    ├── models/             # Business Logic Layer
    │   ├── base_model.py
    │   ├── user.py
    │   ├── place.py
    │   ├── review.py
    │   └── amenity.py
    ├── services/           # Facade
    │   ├── __init__.py     # Shared singleton instance
    │   └── facade.py
    ├── persistence/        # Persistence Layer
    │   └── repository.py
    └── api/
        └── v1/             # Presentation Layer
            ├── users.py
            ├── places.py
            ├── reviews.py
            └── amenities.py
```

### The Factory Pattern — `create_app()`

Flask is not instantiated directly at the global level. A `create_app()` factory function creates and configures the app. This allows multiple instances with different configs (dev, test, prod).

```python
def create_app():
    app = Flask(__name__)
    api = Api(app, version='1.0', title='HBnB API')
    api.add_namespace(users_ns,     path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns,    path='/api/v1/places')
    api.add_namespace(reviews_ns,   path='/api/v1/reviews')
    return app
```

---

## 3. Task 1 — Business Logic Classes

The 4 main domain entities are implemented with full validations, relationships, and methods. These classes are the core of the application.

### 3.1 BaseModel — Shared Parent Class

All entities inherit from `BaseModel`, which provides common attributes and utility methods.

```python
class BaseModel:
    def __init__(self):
        self.id         = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        self.updated_at = datetime.now()

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)  # triggers setter -> all validations run
        self.save()

    def is_max_length(self, name, value, max_length):
        if len(value) > max_length:
            raise ValueError(f'{name} must be {max_length} characters max.')

    def is_between(self, name, value, min, max):
        if not min <= value <= max:
            raise ValueError(f'{name} must be between {min} and {max}.')
```

`is_max_length()` and `is_between()` are shared utility helpers — without them, the same validation code would be copy-pasted across all entities (DRY violation).

### 3.2 Encapsulation — Getters & Setters

Encapsulation hides internal data and forces all access through controlled methods. This implements the **fail-fast** principle: invalid data raises an error immediately at assignment time.

```python
@property
def first_name(self):
    return self.__first_name  # GETTER

@first_name.setter
def first_name(self, value):
    if not isinstance(value, str):
        raise TypeError('First name must be a string')
    super().is_max_length('First name', value, 50)
    self.__first_name = value  # stored ONLY if all validations pass
```

The double underscore `__` makes the attribute private via Python name-mangling (`_User__first_name`). Equivalent to `private` in Java.

### 3.3 User

| Attribute | Type | Validation |
|---|---|---|
| `first_name` | string | required, max 50 chars |
| `last_name` | string | required, max 50 chars |
| `email` | string | valid format (regex), **UNIQUE** across the app |
| `is_admin` | bool | True/False only, default False |

**Email uniqueness** — `User.emails` is a **class attribute** (shared across all instances). If it were `self.emails` in `__init__`, each user would have its own empty set and cross-user duplicate detection would be impossible.

```python
class User(BaseModel):
    emails = set()  # ONE set shared by ALL User instances

    @email.setter
    def email(self, value):
        if not re.match(r'[^@]+@[^@]+\.[^@]+', value):
            raise ValueError('Invalid email format')
        if value in User.emails:
            raise ValueError('Email already exists')
        if hasattr(self, '_User__email'):   # handle email update
            User.emails.discard(self.__email)
        self.__email = value
        User.emails.add(value)
```

### 3.4 Place

| Attribute | Type | Validation |
|---|---|---|
| `title` | string | non-empty, max 100 chars |
| `price` | float/int | >= 0 |
| `latitude` | float | between -90 and 90 |
| `longitude` | float | between -180 and 180 |
| `owner` | User instance | must be a real User object, not a string ID |

Two serialization methods:
- `to_dict()` — lightweight, for list responses (`owner_id` only)
- `to_dict_list()` — full detail, for single-item responses (complete owner, amenities, reviews)

### 3.5 Review

| Attribute | Type | Validation |
|---|---|---|
| `text` | string | non-empty |
| `rating` | int | between 1 and 5 |
| `place` | Place instance | must be a real Place object |
| `user` | User instance | must be a real User object |

Storing real objects (not IDs) means `review.place.title` is accessible directly — no extra repository lookup needed.

### 3.6 Amenity

| Attribute | Type | Validation |
|---|---|---|
| `name` | string | non-empty, max 50 chars |

---

## 4. Repository Pattern — Persistence Layer

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def add(self, obj): pass
    @abstractmethod
    def get(self, obj_id): pass
    @abstractmethod
    def get_all(self): pass
    @abstractmethod
    def update(self, obj_id, data): pass
    @abstractmethod
    def delete(self, obj_id): pass
    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value): pass
```

`ABC` forces every subclass to implement all 6 methods. Forgetting one raises an error at instantiation — all implementations are guaranteed to respect the same contract.

```python
class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}  # plain Python dict { id: object }

    def add(self, obj):
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)  # None if not found

    def get_by_attribute(self, attr_name, attr_value):
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name) == attr_value),
            None
        )
```

All data is lost on restart — intentional for Part 2 to validate architecture before adding database complexity.

**In Part 3:** `SQLRepository(Repository)` will implement the same 6 methods with SQLAlchemy. The Facade swaps `InMemoryRepository` for `SQLRepository` — endpoints change nothing.

---

## 5. The Facade Pattern

The Facade is the **single communication point** between endpoints and models. Classic Gang of Four Design Pattern.

```
Endpoint  →  Facade  →  Repository
              ↓
            Model (validates)
```

| Without Facade | With Facade |
|---|---|
| DB logic scattered in every endpoint | DB logic centralized in Facade only |
| Changing DB = modifying every endpoint | Changing DB = one line in Facade |

```python
class HBnBFacade:
    def __init__(self):
        self.user_repo    = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.place_repo   = InMemoryRepository()
        self.review_repo  = InMemoryRepository()

        # In Part 3, only this changes:
        # self.user_repo = SQLRepository(User)
```

### Example — `create_place()`

```python
def create_place(self, place_data):
    # 1. Validate owner exists and retrieve the object
    user = self.user_repo.get_by_attribute('id', place_data['owner_id'])
    if not user:
        raise KeyError('Invalid input data')

    # 2. Replace owner_id with the real User object
    del place_data['owner_id']
    place_data['owner'] = user

    # 3. Extract amenities
    amenities = place_data.pop('amenities', None)

    # 4. Create Place (triggers all validations via setters)
    place = Place(**place_data)
    self.place_repo.add(place)

    # 5. Maintain bidirectional relations
    user.add_place(place)
    if amenities:
        for amenity in amenities:
            place.add_amenity(amenity)

    return place
```

**Shared singleton** — one Facade instance is created in `app/services/__init__.py` and imported by all endpoints. Without a shared instance, each endpoint would have its own empty storage.

```python
# app/services/__init__.py
from app.services.facade import HBnBFacade
facade = HBnBFacade()  # ONE instance for the entire app
```

---

## 6. API Endpoints

### 6.1 Users

| Method | Endpoint | Status Codes |
|---|---|---|
| `POST` | `/api/v1/users/` | 201 / 400 |
| `GET` | `/api/v1/users/` | 200 |
| `GET` | `/api/v1/users/<id>` | 200 / 404 |
| `PUT` | `/api/v1/users/<id>` | 200 / 404 / 400 |

> No DELETE for users in Part 2 — explicit constraint from the spec.

### 6.2 Amenities

| Method | Endpoint | Status Codes |
|---|---|---|
| `POST` | `/api/v1/amenities/` | 201 / 400 |
| `GET` | `/api/v1/amenities/` | 200 |
| `GET` | `/api/v1/amenities/<id>` | 200 / 404 |
| `PUT` | `/api/v1/amenities/<id>` | 200 / 404 / 400 |

> Name uniqueness check added beyond the spec — prevents duplicate entries like 3x "WiFi".

### 6.3 Places

| Method | Endpoint | Status Codes |
|---|---|---|
| `POST` | `/api/v1/places/` | 201 / 400 |
| `GET` | `/api/v1/places/` | 200 (lightweight: id, title, lat, lon only) |
| `GET` | `/api/v1/places/<id>` | 200 / 404 (full: owner + amenities + reviews) |
| `PUT` | `/api/v1/places/<id>` | 200 / 404 / 400 |
| `GET` | `/api/v1/places/<id>/reviews` | 200 / 404 |

> List vs Detail: the list endpoint returns only `id, title, latitude, longitude` per the spec. Full detail is only available on GET by ID — standard REST optimization.

### 6.4 Reviews

| Method | Endpoint | Status Codes |
|---|---|---|
| `POST` | `/api/v1/reviews/` | 201 / 400 |
| `GET` | `/api/v1/reviews/` | 200 |
| `GET` | `/api/v1/reviews/<id>` | 200 / 404 |
| `PUT` | `/api/v1/reviews/<id>` | 200 / 404 / 400 |
| `DELETE` | `/api/v1/reviews/<id>` | 200 / 404 |

**Anti-self-review rule** (added beyond the spec):
```python
if place.owner.id == user.id:
    return {'error': 'User cannot review their own place'}, 400
```

**Clean delete** — removes the review from 3 places:
```python
def delete_review(self, review_id):
    review = self.review_repo.get(review_id)
    user   = self.user_repo.get(review.user.id)
    place  = self.place_repo.get(review.place.id)

    user.delete_review(review)          # 1. remove from user's list
    place.delete_review(review)         # 2. remove from place's list
    self.review_repo.delete(review_id)  # 3. remove from repo
```

Removing only from the repo would leave dead references in User and Place — future bugs guaranteed.

---

## 7. flask-restx — Key Contributions

### 7.1 Automatic Input Validation

```python
user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
    'email':      fields.String(required=True)
})

@api.expect(user_model, validate=True)
def post(self):
    ...
```

`validate=True` — if the incoming JSON is missing required fields, flask-restx automatically returns a `400` without entering the method. No manual field checking needed.

### 7.2 Automatic Swagger Documentation

Flask-restx auto-generates a Swagger UI at `/api/v1/`. Every endpoint is documented with its parameters, responses, and status codes — zero extra documentation code.

### 7.3 Endpoint Structure

```python
@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    def post(self):
        user_data = api.payload
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400
        try:
            new_user = facade.create_user(user_data)
            return new_user.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400
```

The `try/except` catches all errors raised by setter validations (`TypeError`, `ValueError`) and returns a clean `400` response instead of crashing.

---

## 8. Task 6 — Tests

### 8.1 Unit Tests — 25 total

| File | Tests | What's covered |
|---|---|---|
| `test_user.py` | 5 | valid creation, invalid email, duplicate email, name too long, is_admin not bool |
| `test_place.py` | 8 | creation, empty title, title too long, negative price, invalid lat/lon, owner not User, to_dict |
| `test_amenity.py` | 5 | creation, empty name, name not string, name too long, to_dict |
| `test_review.py` | 7 | creation, empty text, invalid rating, rating not int, place/user not correct type, to_dict |

### 8.2 The `clear_emails` Fixture — Why It's Essential

```python
@pytest.fixture(autouse=True)
def clear_emails():
    User.emails.clear()  # wipe the class-level set between each test
    yield
```

`User.emails` is a class attribute — it **persists between tests**. Without this fixture, an email created in `test_user_creation()` would still be in `User.emails` for `test_duplicate_email()`, causing false positives. `autouse=True` applies it to every test automatically.

### 8.3 Running Tests

```bash
cd part2
python -m pytest tests/
# Expected: 25 passed
```

> Always run from the `part2` folder, not from inside `tests/`. Otherwise Python cannot find the `app` module and all imports fail with `ModuleNotFoundError`.

---

## 9. Running the Application

```bash
# Install dependencies
pip install flask flask-restx

# Start the server
cd part2
python run.py

# Access Swagger UI
open http://localhost:5000/api/v1/

# Run unit tests
python -m pytest tests/
```

---


Authors

Frances Palmer  - https://github.com/FrancesMP
Yohhny Marcelus - https://github.com/youri47
Sedra Ramarosaona - https://github.com/SedraR78