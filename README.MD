# Blog Poster — Backend API

A production-style, fully asynchronous **Blog / Content Management backend** built with **FastAPI**, **MySQL**, and **SQLAlchemy (async)**. It provides a complete authentication system (JWT access/refresh tokens, role-based authorization, OTP-based password reset via email) and a full blog post management module with image uploads to Cloudinary, soft-delete lifecycle, search, and pagination.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [High-Level Architecture](#high-level-architecture)
- [Project Structure](#project-structure)
- [Request Lifecycle (How a Request Flows)](#request-lifecycle-how-a-request-flows)
- [Database Design (Models)](#database-design-models)
- [Authentication & Authorization](#authentication--authorization)
  - [Registration](#1-registration)
  - [Login (JWT Issuance)](#2-login-jwt-issuance)
  - [Token Refresh](#3-token-refresh)
  - [Authenticated Requests](#4-authenticated-requests)
  - [Role-Based Authorization (RBAC)](#5-role-based-authorization-rbac)
  - [Forgot / Reset Password (OTP Flow)](#6-forgot--reset-password-otp-flow)
  - [Automatic Admin Seeding](#7-automatic-admin-seeding)
- [Blog Posts Module](#blog-posts-module)
  - [Post Lifecycle (Status Machine)](#post-lifecycle-status-machine)
  - [Image Uploads (Cloudinary)](#image-uploads-cloudinary)
  - [Search & Pagination](#search--pagination)
- [API Reference](#api-reference)
- [Exception Handling](#exception-handling)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [Getting Started](#getting-started)
- [Testing](#testing)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | **FastAPI** (async, lifespan-managed) |
| Server | **Uvicorn** (`uvicorn[standard]`) |
| Database | **MySQL** via **SQLAlchemy 2.x (asyncio)** + **aiomysql** / **PyMySQL** drivers |
| ORM / Migrations | SQLAlchemy `declarative_base` with `Base.metadata.create_all` on startup |
| Auth | **PyJWT** (access + refresh tokens, separate signing keys), **bcrypt** (password hashing), OAuth2 Password Bearer |
| Validation | **Pydantic v2** (`pydantic[email]`, `ConfigDict(from_attributes=True)`) |
| Email | **aiosmtplib** — async OTP delivery through Gmail SMTP (port 465, TLS) |
| Media Storage | **Cloudinary** — blog post image hosting (`blog_posts` folder) |
| Testing | **pytest**, **pytest-asyncio**, **httpx**, `unittest.mock` |
| Config | **python-dotenv** + a central `Settings` class |

---

## High-Level Architecture

The project follows a strict **layered (n-tier) architecture** with clear separation of concerns and **dependency injection** throughout. Each layer only talks to the layer directly below it, and lower layers are consumed through **abstract interfaces** (Dependency Inversion Principle).

```
┌─────────────────────────────────────────────────────────────┐
│  CONTROLLERS  (app/controller/)                             │
│  FastAPI routers — HTTP concerns only: parsing requests,    │
│  auth guards, response models, status codes.                │
└──────────────────────────┬──────────────────────────────────┘
                           │ depends on
┌──────────────────────────▼──────────────────────────────────┐
│  SERVICES  (app/service/)                                   │
│  Business logic: registration, login, token refresh,        │
│  password reset, post lifecycle rules, ownership checks.    │
│  Services depend on repository INTERFACES, not concrete DB. │
└──────────────────────────┬──────────────────────────────────┘
                           │ implements
┌──────────────────────────▼──────────────────────────────────┐
│  REPOSITORIES  (app/repository/)                            │
│  Data access only — SQLAlchemy queries against the async    │
│  session. Defined by abstract interfaces:                   │
│  IUserRepository, IPostRepository.                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  MODELS  (app/model/)  →  MySQL database                    │
│  SQLAlchemy ORM entities: users, posts, password_resets.    │
└─────────────────────────────────────────────────────────────┘
```

**Supporting layers:**

- **`app/schemas/`** — Pydantic DTOs decoupling the API contract from the DB models.
- **`app/middleware/`** — Authentication (JWT verification) and role-based authorization guards.
- **`app/core/`** — Cross-cutting infrastructure: config, DB engine/session, security (hashing/JWT), email, Cloudinary, admin seeding, FastAPI dependencies.
- **`app/exceptions_handling/`** — A custom exception hierarchy mapped to HTTP responses by a global exception handler.

**Why interfaces?** `AuthService` depends on `IUserRepository` and `PostService` depends on `IPostRepository` — both ABCs. This makes the business logic fully unit-testable with mocks (see `tests/`) and allows the persistence implementation to be swapped without touching services.

---

## Project Structure

```
Blog-Poster-Project/
├── main.py                        # App entrypoint: lifespan, DB init, global exception handler
├── requirements.txt
├── pytest.ini
├── .env                           # Environment secrets (never committed)
│
├── app/
│   ├── core/                      # Infrastructure & cross-cutting concerns
│   │   ├── config.py              # Settings loaded from environment variables
│   │   ├── db.py                  # Async engine, session factory, get_db_session dependency
│   │   ├── security.py            # bcrypt hashing + JWT create/decode helpers
│   │   ├── dependecies.py         # get_current_user (OAuth2 bearer → UserModel)
│   │   ├── email.py               # OTP generation + async Gmail SMTP sending
│   │   ├── cloudinary_util.py     # Cloudinary config + image upload helper
│   │   └── seed.py                # Seeds the first ADMIN user on startup
│   │
│   ├── middleware/
│   │   ├── auth.py                # authenticate(): verifies Bearer access token
│   │   └── roles.py               # authorize_roles([...]): RBAC guard factory
│   │
│   ├── model/                     # SQLAlchemy ORM models
│   │   ├── user_model.py          # UserModel + Role enum (user/admin)
│   │   ├── posts_model.py         # Posts_Model + PostStatus enum
│   │   └── password_reset_model.py# PasswordResetModel (OTP storage)
│   │
│   ├── schemas/                   # Pydantic request/response DTOs
│   │   ├── user_schema.py
│   │   └── posts_schema.py
│   │
│   ├── repository/                # Data-access layer
│   │   ├── base.py                # IUserRepository (ABC)
│   │   ├── interfaces/
│   │   │   └── post_repo_interface.py  # IPostRepository (ABC)
│   │   ├── user_repository.py     # UserRepository (SQLAlchemy impl)
│   │   └── posts_repository.py    # PostRepository (SQLAlchemy impl)
│   │
│   ├── service/                   # Business-logic layer
│   │   ├── user_service.py        # AuthService
│   │   └── posts_service.py       # PostService
│   │
│   ├── controller/                # HTTP layer (routers)
│   │   ├── user_controller.py     # /auth/* endpoints
│   │   └── posts_controller.py    # /posts/* endpoints
│   │
│   ├── routers/
│   │   └── router.py              # Central api_router aggregating all controllers
│   │
│   └── exceptions_handling/
│       └── exceptions.py          # AppExceptions hierarchy (typed, status-coded)
│
└── tests/                         # pytest suite (unit tests with mocked sessions)
    ├── conftest.py                # Test env vars + mock AsyncSession fixture
    ├── test_user.py               # AuthService tests (register/login/refresh/OTP)
    ├── test_posts.py              # PostService tests
    ├── test_security.py           # Hashing + JWT tests
    ├── test_middleware.py         # authenticate / authorize_roles tests
    ├── test_email.py              # OTP email tests
    ├── test_cloudinary.py         # Upload helper tests
    ├── test_db_seed.py            # Admin seeding tests
    ├── test_exceptions.py         # Exception contract tests
    └── dependencies.py
```

---

## Request Lifecycle (How a Request Flows)

Using `POST /api/v1/posts/create-posts` as an example:

1. **Uvicorn** receives the HTTP request → FastAPI routes it via the central `api_router` (mounted at `/api/v1` in `main.py`).
2. **Controller** (`posts_controller.py`) parses `multipart/form-data` (`title`, `content`, optional `image` file).
3. **Dependencies run first:**
   - `get_db_session` opens an async SQLAlchemy session (closed automatically after the request).
   - `get_current_user` extracts the `Authorization: Bearer <token>` header via OAuth2PasswordBearer, decodes the JWT, and loads the `UserModel` from MySQL.
4. **Controller builds a DTO** (`PostCreate`) and constructs the service with a repository: `PostService(PostRepository(session))`.
5. **Service** (`PostService.create_post`) runs business rules: uploads the image to Cloudinary if present, sets initial status to `PUBLISHED`, attaches `user_id`.
6. **Repository** persists the `Posts_Model` and commits.
7. The result flows back up and is serialized through **`PostResponse`** (Pydantic, `from_attributes=True`) → JSON response.
8. Any raised `AppExceptions` subclass is caught by the **global exception handler** in `main.py` and returned as a uniform JSON error envelope.

---

## Database Design (Models)

### `users` — `UserModel`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK, indexed | |
| `email` | String(255), unique, indexed, not null | Login identifier |
| `hashed_password` | String(255), not null | bcrypt hash |
| `role` | String(50), default `user` | `user` or `admin` (`Role` enum) |
| `first_name` / `last_name` | String, nullable | Profile fields |
| `phone_number` | String(20), nullable | Profile field |

Relationship: one-to-many → `posts`.

### `posts` — `Posts_Model`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK, indexed | |
| `title` | String(255), not null | |
| `content` | Text, not null | |
| `image_url` | String(500), nullable | Cloudinary secure URL |
| `status` | Enum(`PUBLISHED`, `UNPUBLISHED`, `DELETED`) | Defaults to `PUBLISHED`; soft-delete lifecycle |
| `user_id` | Integer, FK → `users.id`, not null | Owner |

Relationship: many-to-one → `owner` (`UserModel`).

### `password_resets` — `PasswordResetModel`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `email` | String(255), indexed | Target account |
| `otp_code` | String(10) | 6-digit OTP |
| `expires_at` | DateTime | OTP validity window (10 minutes) |
| `is_used` | Boolean, default `False` | Prevents OTP replay |

> **Note:** The `users` and `posts` tables are created automatically at startup via `Base.metadata.create_all`, and the database itself is created if missing (`CREATE DATABASE IF NOT EXISTS` with `utf8mb4`).

---

## Authentication & Authorization

Security is built around **dual JWT tokens** and **role-based access control**, with **bcrypt** for password storage.

### 1. Registration

`POST /api/v1/auth/register`

- The controller validates the body with `UserRegisterSchema` (`email`, `password`).
- `AuthService.register` checks for an existing user with that email → raises `UserAlreadyExistsException` (HTTP 409) if taken.
- The password is hashed with **bcrypt** (`hash_password` in `app/core/security.py`) — plaintext is never stored.
- A `UserModel` is created with `role = user` and persisted via `UserRepository`.
- Returns `201 Created` with `UserResponseSchema` (never includes the password).

**Admin registration:** `POST /api/v1/auth/register-admin` does the same but assigns `role = admin`. It is protected — only an existing **ADMIN** can create another admin (see [RBAC](#5-role-based-authorization-rbac)). The very first admin is seeded automatically at startup (see below).

### 2. Login (JWT Issuance)

`POST /api/v1/auth/login`

1. The user is looked up by email; the supplied password is verified against the stored bcrypt hash using `verify_password`. Any mismatch raises `InvalidCredentialsException` (HTTP 401) — the error intentionally does not reveal whether the email or the password was wrong.
2. On success, a payload is built:
   ```json
   { "sub": "<email>", "user_id": <id>, "role": "<user|admin>" }
   ```
3. **Two tokens are signed with two different secrets** (`app/core/security.py`):

   | Token | Signed with | Lifetime | `type` claim |
   |---|---|---|---|
   | Access token | `JWT_ACCESS_TOKEN` | `ACCESS_TOKEN_EXPIRE_MINUTES` (short-lived) | `"access"` |
   | Refresh token | `JWT_REFRESH_TOKEN` | `REFRESH_TOKEN_EXPIRE_DAYS` (long-lived) | `"refresh"` |

   Both use the algorithm from `JWT_ALGORITHM` (e.g. `HS256`) and carry an `exp` expiry claim (UTC).
4. Response (`TokenResponseSchema`):
   ```json
   {
     "access_token": "...",
     "refresh_token": "...",
     "role": "user",
     "token_type": "bearer"
   }
   ```

### 3. Token Refresh

`POST /api/v1/auth/refresh`

- Accepts `{ "refresh_token": "..." }`.
- The token is decoded with the **refresh** secret; the service verifies the `type` claim is `"refresh"` (an access token cannot be used here).
- A **new access token** is issued from the embedded claims (`sub`, `user_id`, `role`). The same refresh token is returned unchanged.
- Expired/invalid refresh tokens → HTTP 401.

This means users stay logged in for days (refresh window) while API access tokens remain short-lived, limiting exposure if an access token leaks.

### 4. Authenticated Requests

Clients send the access token on every protected request:

```
Authorization: Bearer <access_token>
```

Two equivalent guards exist:

- **`get_current_user`** (`app/core/dependecies.py`) — uses FastAPI's `OAuth2PasswordBearer`, decodes the token, extracts `user_id`, and **loads the full `UserModel` from the database** (verifying the user still exists). Raises `InvalidCredentialsException` (401) on missing/invalid/expired tokens. Used by `POST /posts/create-posts`.
- **`authenticate`** (`app/middleware/auth.py`) — manually parses the `Authorization` header, enforces the `Bearer ` scheme, decodes the token, and additionally **enforces `type == "access"`** so refresh tokens can't be used to call the API. Returns the JWT payload dict.

### 5. Role-Based Authorization (RBAC)

`authorize_roles(allowed_roles)` (`app/middleware/roles.py`) is a **guard factory** built on top of `authenticate`:

```python
@router.get("/profile")
async def get_my_profile(current_user: dict = Depends(authorize_roles([Role.USER, Role.ADMIN]))):
    ...
```

- It runs `authenticate` first (token must be valid).
- Then compares the token's `role` claim against the allowed list.
- Mismatch → **HTTP 403 Forbidden** with a message listing the allowed roles.

Applied throughout the API:

| Endpoint | Allowed roles |
|---|---|
| `POST /auth/register-admin` | `ADMIN` |
| `GET/PUT /auth/profile` | `USER`, `ADMIN` |
| `PUT /posts/update-posts/{id}` | `USER` |
| `PATCH /posts/unpublish/{id}` | `USER` |
| `PATCH /posts/delete/{id}` | `USER` |
| `GET /posts/get-all/{user_id}` | `USER` |
| `GET /posts/get-all-posts` | `USER` |

### 6. Forgot / Reset Password (OTP Flow)

**Step 1 — Request OTP:** `POST /api/v1/auth/forgot-password`

1. `AuthService.request_password_reset` verifies the email belongs to an existing user.
2. A cryptographically secure **6-digit OTP** is generated (`secrets.randbelow`).
3. A `PasswordResetModel` row is saved with a **10-minute expiry** and `is_used = False`.
4. The OTP email is sent **in the background** (FastAPI `BackgroundTasks`) via **Gmail SMTP over TLS** (`aiosmtplib`, port 465) so the API responds immediately.
5. Response is deliberately vague: `"If this email exists, an OTP has been sent."` — preventing user enumeration.

**Step 2 — Reset with OTP:** `POST /api/v1/auth/reset-password`

1. The service looks up a **valid OTP**: matching email + code, `is_used == False`, and `expires_at >= now`.
2. Invalid/expired → HTTP 400.
3. On success: the user's password is re-hashed with bcrypt, and the OTP is **marked as used** (replay protection).

### 7. Automatic Admin Seeding

On application startup (`lifespan` in `main.py`):

1. The MySQL database is created if it doesn't exist (`utf8mb4`).
2. All tables are created via `Base.metadata.create_all`.
3. `seed_initial_admin` checks whether **any** admin exists; if not, it creates one using `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` (bcrypt-hashed). This guarantees the system always has a bootstrap admin without manual DB inserts.

---

## Blog Posts Module

### Post Lifecycle (Status Machine)

Posts are **never hard-deleted**; they move through a status enum (`PostStatus`):

```
        create
          │
          ▼
     PUBLISHED ──(unpublish)──► UNPUBLISHED ──(delete)──► DELETED
          ▲                         │
          └────────(republish)──────┘
```

Enforced rules (`PostService`):

- **Create** → always starts as `PUBLISHED`, owned by the authenticated user.
- **Update** → only allowed when the post is in `UNPUBLISHED` state (you must unpublish before editing); a `DELETED` post raises `PostAlreadyDeletedException` (400); missing posts raise `PostsNotFoundException` (404); modifying another user's post raises `PostAccessDeniedException` (403).
- **Unpublish / Republish** (`PATCH /posts/unpublish/{id}`) → toggles `PUBLISHED ⇄ UNPUBLISHED`.
- **Delete** (`PATCH /posts/delete/{id}`) → only from `UNPUBLISHED` → `DELETED` (soft delete). The row remains in MySQL.
- **Public listing** (`GET /posts/get-all-posts`) → only returns `PUBLISHED` posts.

### Image Uploads (Cloudinary)

- Post create/update endpoints accept `multipart/form-data` with an optional `image` file.
- The file stream is uploaded to **Cloudinary** (`blog_posts` folder) via `upload_image_to_cloudinary`, and the returned `secure_url` is stored in `posts.image_url`.
- Failures raise `CloudinaryConnectingError` (HTTP 502).

### Search & Pagination

Both listing endpoints support:

- `search` — case-insensitive partial match (`ILIKE %...%`) against **title OR content**.
- `page` (≥ 1, default 1) and `limit` (1–100, default 10) — converted to SQL `LIMIT`/`OFFSET`.
- Results are ordered newest-first (`id DESC`).

---

## API Reference

Base URL: **`/api/v1`** — interactive docs available at `/docs` (Swagger UI) and `/redoc` when running.

### Authentication — `/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | Public | Register a new user (role = `user`) |
| `POST` | `/auth/register-admin` | **ADMIN** | Register a new admin user |
| `POST` | `/auth/login` | Public | Login → `{ access_token, refresh_token, role }` |
| `POST` | `/auth/refresh` | Public (refresh token) | Exchange refresh token for a new access token |
| `GET` | `/auth/profile` | USER / ADMIN | Get the current user's profile |
| `PUT` | `/auth/profile` | USER / ADMIN | Update `first_name`, `last_name`, `phone_number` |
| `POST` | `/auth/forgot-password` | Public | Send a 6-digit OTP to the user's email |
| `POST` | `/auth/reset-password` | Public | Reset password with email + OTP + new password |

### Posts — `/posts`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/posts/create-posts` | Bearer token | Create a post (form-data: `title`, `content`, optional `image`) |
| `PUT` | `/posts/update-posts/{posts_id}` | USER | Update an unpublished post (form-data, optional new image) |
| `PATCH` | `/posts/unpublish/{posts_id}` | USER | Toggle `PUBLISHED ⇄ UNPUBLISHED` |
| `PATCH` | `/posts/delete/{posts_id}` | USER | Soft-delete an unpublished post (`→ DELETED`) |
| `GET` | `/posts/get-all/{user_id}` | USER | List the current user's posts (`search`, `page`, `limit`) |
| `GET` | `/posts/get-all-posts` | USER | List all published posts (`search`, `page`, `limit`) |

### Example: Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "role": "user",
  "token_type": "bearer"
}
```

### Example: Create a Post

```bash
curl -X POST http://localhost:8000/api/v1/posts/create-posts \
  -H "Authorization: Bearer <access_token>" \
  -F "title=My First Post" \
  -F "content=Hello world!" \
  -F "image=@cover.png"
```

---

## Exception Handling

All domain errors derive from `AppExceptions` (`app/exceptions_handling/exceptions.py`), each carrying a `message` and an HTTP `status_code`. A **global handler** registered in `main.py` converts them into a consistent error envelope:

```json
{
  "success": false,
  "error_code": "UserAlreadyExistsException",
  "message": "User with email 'a@b.com' already exists."
}
```

| Exception | Status |
|---|---|
| `InvalidCredentialsException`, `TokenExpiredException`, `InvalidTokenException` | 401 |
| `AccountInactiveException`, `PostAccessDeniedException` | 403 |
| `UserNotFoundException`, `PostsNotFoundException` | 404 |
| `UserAlreadyExistsException` | 409 |
| `PasswordResetTokenInvalidException`, `InvalidPostStatusException`, `PostAlreadyDeletedException` | 400 |
| `FileSizeExceededException` (413), `InvalidFileFormatException` (415), `InvalidPostsType` (422) | 4xx |
| `EnvLoadingError`, `OTPGeneratingError` | 500 |
| `ImageUploadFailedException`, `CloudinaryConnectingError`, `SendingEmailFailed` | 502 |

---

## Configuration & Environment Variables

Configuration is centralized in `app/core/config.py` (loaded from `.env` via `python-dotenv`). Required variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async MySQL DSN, e.g. `mysql+aiomysql://root:password@localhost:3306/blog_db` |
| `JWT_ACCESS_TOKEN` | Secret key for signing **access** tokens |
| `JWT_REFRESH_TOKEN` | Secret key for signing **refresh** tokens (use a *different* value) |
| `JWT_ALGORITHM` | JWT algorithm (e.g. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (e.g. `15`) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (e.g. `7`) |
| `FIRST_ADMIN_EMAIL` | Email for the auto-seeded bootstrap admin |
| `FIRST_ADMIN_PASSWORD` | Password for the bootstrap admin (stored bcrypt-hashed) |
| `GMAIL` | Gmail address used to send OTP emails |
| `GMAIL_SMTP_KEY` | Gmail **App Password** for SMTP auth |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

---

## Getting Started

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd Blog-Poster-Project

# 2. Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Create your .env file (see table above)

# 4. Make sure MySQL is running — the database, tables, and the
#    first admin user are all created automatically on startup.

# 5. Run the API
uvicorn main:app --reload
```

- API root: `http://localhost:8000/api/v1`
- Swagger UI: `http://localhost:8000/docs`

On first boot the app will: create the database → create tables → seed the initial admin (`FIRST_ADMIN_EMAIL`). Log in with those credentials, then use `/auth/register-admin` to create additional admins.

---

## Testing

The `tests/` suite (~1,600 lines) uses **pytest + pytest-asyncio** with mocked async sessions (`conftest.py` provides a `mock_async_session` fixture and safe test environment variables), so tests run **without a real database, SMTP server, or Cloudinary account**.

```bash
pytest            # run the full suite
pytest -v         # verbose
```

Coverage includes:

- `test_user.py` — registration, duplicate-email rejection, login, token refresh, profile update, OTP request/reset flows
- `test_posts.py` — post creation (with/without image), lifecycle transitions, access denial, search/pagination
- `test_security.py` — bcrypt hashing/verification, JWT creation/decoding, expiry
- `test_middleware.py` — header parsing, token-type enforcement, role guards
- `test_email.py`, `test_cloudinary.py`, `test_db_seed.py`, `test_exceptions.py`

## Author

- Dilan Uddeepika Liyanaarachchi

