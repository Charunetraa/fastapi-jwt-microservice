JWT Authentication Microservice

A RESTful API built using FastAPI with JWT authentication, bcrypt password hashing, SQLite persistence, and secure CRUD operations.

Features

- User registration and login
- Password hashing using bcrypt
- JWT-based authentication
- Protected item CRUD endpoints
- Request validation using Pydantic
- SQLite database with SQLAlchemy
- Interactive Swagger documentation

Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- bcrypt
- Pydantic
- Uvicorn

Project Structure

fastapi-jwt-microservice/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── .env
├── .gitignore
└── README.md

Run the Project

Install the dependencies in your virtual environment, then start the server:

.\.venv\Scripts\python.exe -m uvicorn app.main:app

Open the API documentation:

http://127.0.0.1:8000/docs

API Endpoints

Method| Endpoint| Description
POST| "/auth/register"| Register a user
POST| "/auth/login"| Login and receive JWT
POST| "/items"| Create an item
GET| "/items"| List the user's items
GET| "/items/{item_id}"| Get an item
PUT| "/items/{item_id}"| Update an item
DELETE| "/items/{item_id}"| Delete an item

Item endpoints require JWT Bearer authentication.

Testing

The API was tested using Swagger UI. Registration, login, and item CRUD operations were verified with successful responses.

Security Notes

- Passwords are stored as bcrypt hashes.
- Protected endpoints require a valid JWT access token.
- The ".env" file contains the secret key and must not be committed to GitHub.