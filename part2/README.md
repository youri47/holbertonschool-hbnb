HBnB Part 2 — Business Logic & API Endpoints

Table of Contents

Description
Architecture
Technologies
Installation
Running the App
API Endpoints
Usage Examples
Data Validations
Running Tests
Authors


Description

HBnB is an Airbnb-like web application built with Python and Flask. Part 2 implements the Business Logic Layer and the RESTful API endpoints on top of the UML design from Part 1.
The app follows a clean 3-layer architecture that separates concerns and makes the codebase easy to extend — in Part 3, the in-memory storage will be swapped for a real SQL database without touching the endpoints or models.

Architecture
part2/
├── run.py                        # Entry point
├── config.py                     # Flask configuration
├── requirements.txt
└── app/
    ├── __init__.py               # App factory (create_app)
    ├── api/
    │   └── v1/
    │       ├── users.py          # User endpoints
    │       ├── places.py         # Place endpoints
    │       ├── reviews.py        # Review endpoints
    │       └── amenities.py      # Amenity endpoints
    ├── models/                   # Business Logic Layer
    │   ├── baseModel.py          # Base class (id, timestamps, helpers)
    │   ├── user.py
    │   ├── place.py
    │   ├── review.py
    │   └── amenity.py
    ├── services/
    │   └── facade.py             # Facade — bridges API and models
    └── persistence/
        └── repository.py         # Abstract repo + InMemoryRepository
How the layers interact
Client Request
      │
      ▼
Presentation Layer (api/)
  - Receives HTTP request
  - Validates input format with flask-restx
  - Calls the Facade
      │
      ▼
Facade (services/facade.py)
  - Resolves relationships (owner_id → User object)
  - Orchestrates creation, update, deletion
  - Calls the Repository
      │
      ▼
Persistence Layer (persistence/repository.py)
  - Stores and retrieves objects
  - In Part 2: in-memory Python dict
  - In Part 3: SQLAlchemy
      │
      ▼
Business Logic Layer (models/)
  - Validates all data via getters/setters
  - Raises TypeError / ValueError on invalid input

Technologies

Python 3.10+
Flask — web framework
Flask-RESTX — REST API + automatic Swagger documentation
pytest — unit testing
uuid4 — unique ID generation for all entities


Installation

bash# Clone the repository
git clone https://github.com/your-username/holbertonschool-hbnb-3.git
cd holbertonschool-hbnb-3/part2

# Create and activate a virtual environment 
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

Running the App
bashpython run.py

API base URL: http://127.0.0.1:5000/api/v1/
Swagger UI (interactive docs): http://127.0.0.1:5000/api/v1/


The app runs in debug mode by default — do not use in production.


API Endpoints
Users /api/v1/users

POST / — Create a user — 201 400
GET / — List all users — 200
GET /<id> — Get user by ID — 200 404
PUT /<id> — Update a user — 200 400 404

Places /api/v1/places

POST / — Create a place — 201 400
GET / — List all places (id, title, latitude, longitude) — 200
GET /<id> — Get place by ID with full details (owner, amenities, reviews) — 200 404
PUT /<id> — Update a place — 200 400 404
GET /<id>/reviews — Get all reviews for a place — 200 404

Reviews /api/v1/reviews

POST / — Create a review — 201 400
GET / — List all reviews — 200
GET /<id> — Get review by ID — 200 404
PUT /<id> — Update a review — 200 400 404
DELETE /<id> — Delete a review — 200 404

Amenities /api/v1/amenities

POST / — Create an amenity — 201 400
GET / — List all amenities — 200
GET /<id> — Get amenity by ID — 200 404
PUT /<id> — Update an amenity — 200 400 404

Usage Examples

Create a User
curl -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  }'
json{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
Create a Place
curl -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nice flat in Paris",
    "description": "Cozy apartment near the Eiffel Tower",
    "price": 120.0,
    "latitude": 48.8566,
    "longitude": 2.3522,
    "owner_id": "<user_id>",
    "amenities": []
  }'
Create a Review
curl -X POST http://127.0.0.1:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing place, highly recommend!",
    "rating": 5,
    "user_id": "<user_id>",
    "place_id": "<place_id>"
  }'

Note: A user cannot review their own place — the API will return a 400 error.

Delete a Review

curl -X DELETE http://127.0.0.1:5000/api/v1/reviews/<review_id>

Data Validations
All validations are enforced at the model level via getters and setters. Invalid data raises an error immediately before being stored.
User

first_name — required string, max 50 characters
last_name — required string, max 50 characters
email — valid format (must contain @), unique across all users
is_admin — boolean only, defaults to False

Place

title — required, non-empty string, max 100 characters
price — must be a positive number (>= 0)
latitude — float between -90 and 90
longitude — float between -180 and 180
owner — must reference an existing User

Review

text — required, non-empty string
rating — integer between 1 and 5
place — must reference an existing Place
user — must reference an existing User
a user cannot review their own place

Amenity

name — required, non-empty string, max 50 characters

Running Tests
bashcd part2
python -m pytest tests/
Expected output: 25 passed
Test coverage

tests/test_user.py — 5 tests
tests/test_place.py — 8 tests
tests/test_amenity.py — 5 tests
tests/test_review.py — 7 tests


Always run from the part2/ directory — running from tests/ will cause import errors.


Authors

Frances Palmer 
Yohhny Marcelus
Sedra Ramarosaona