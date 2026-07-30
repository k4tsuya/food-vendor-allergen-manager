# Food Vendor Allergen Manager

![Tests](https://github.com/k4tsuya/product_allergies_management/actions/workflows/tests.yml/badge.svg)

## 📌 Project Overview

This project started from a **real, practical need** at my current **part-time job** in a snackbar in the Netherlands.

As a food business, we are legally required to:

* Maintain a clear and correct **allergen list**
* Be able to tell customers **which allergens are present in which items**
* Follow EU / NVWA (Nederlandse Voedsel- en Warenautoriteit) food allergen regulations

Managing this information manually quickly became error‑prone and time‑consuming. This project is my attempt to **solve that real-world problem with software**, while at the same time **learning and exploring new backend and frontend technologies**.

The project was originally built around "products," but has since been generalized to **"items"** — a step toward making this usable by any food vendor (bakery, restaurant, butcher, etc.), not just a snackbar. It now also includes a full **admin area**, so a vendor can manage their own data without touching code.

---

## 🚧 Project Status

This project is **actively under development** and is being built step by step as a learning project.

It is intended to become part of my **developer portfolio**, showcasing how I approach real-world backend problems, data modeling, authentication, and frontend development.

---

## 🎯 Goals of This Project

* Model food allergens **correctly and realistically**
* Link allergens to items in a flexible way
* Create a clean and understandable backend foundation
* Build a working, presentable frontend to consume that backend
* Let a vendor manage their own data through an authenticated admin area, not just seed files
* Learn and practice technologies I have not used deeply before
* Build a meaningful portfolio project based on real business needs
* Generalize the project so any food vendor can use their own deployment of it

---

## 🧠 Domain Modeling

A key design decision in this project is **how allergens are modeled**.

* Allergens are **not boolean fields** on an item
* Allergens are a **fixed, regulated list** (EU / NVWA)
* Items can contain **multiple allergens**
* One allergen can apply to **multiple items**

Because of this, the project uses a **many‑to‑many relationship** between:

* `Item`
* `Allergen`

This approach:

* Matches real‑world legislation
* Avoids fragile database schemas
* Makes the system easy to extend in the future (e.g. "may contain traces of")

The same pattern (a dedicated reference table + many‑to‑many relationship) is reused for **meat types** — an optional feature for tracking which meats (pork, beef, chicken, turkey, horse, fish, lamb) are present in an item.

**Categories** (e.g. "Snacks", "Bakery") work slightly differently: each item has at most one category, referenced by a `category_key` string matching a `Category` record's `code`. Categories, allergens, and meat types are all fully manageable through the admin area — an admin can create, rename, or delete any of them without touching code.

---

## 🧱 Tech Stack

I intentionally chose this tech stack to **learn and explore different tools** beyond what I already knew.

**Backend**
* **Python 3.13**
* **FastAPI** – modern, fast backend framework
* **SQLAlchemy 2.0** – ORM with explicit, type‑safe models
* **SQLite** – local database for development (see **Environment Configuration** for other options)
* **Alembic** – database schema migrations
* **Pydantic** – data validation and API schemas
* **passlib (bcrypt)** – password hashing for the admin account
* **python-jose** – JWT creation and verification
* **slowapi** – rate limiting on the login endpoint
* **pytest** – automated testing, with an isolated in-memory test database
* **ruff** – linting and formatting
* **mypy** – static type checking

**Frontend**
* **React** – component-based UI library
* **Vite** – frontend build tool and dev server
* **React Router** – client-side routing, including nested/protected admin routes

Although I have previous experience with **Django + DRF**, this project focuses on:

* Understanding lower‑level ORM concepts
* Explicit database modeling
* Clear separation between models, schemas, and application logic
* Learning frontend development from the ground up with React
* Practicing authentication and building an authenticated admin area in this stack

---

## 🗂️ Project Structure (backend)

```
src/product_management/
├── core/
│   ├── database.py       # DB engine/session setup + get_db dependency, reads DATABASE_URL from .env
│   ├── security.py         # Password hashing, JWT creation/verification, rate limiter, auth dependency
│   ├── logging_config.py     # Global logging setup (format, level)
│   └── audit.py                # Lightweight audit logging for admin write actions
├── routers/
│   ├── items.py             # /items, /items/pdf routes (search/filter, CRUD)
│   ├── allergens.py          # /allergens routes (public read, authenticated write)
│   ├── meat_types.py          # /meat-types routes (public read, authenticated write)
│   ├── categories.py           # /categories routes (public read, authenticated write)
│   ├── config.py                # /config route — app-wide settings (public read, authenticated write)
│   ├── auth.py                    # /auth/login, /auth/me, /auth/password
│   ├── data.py                      # /data/export, /data/import — full backup/restore
│   └── health.py                    # /health route
├── models.py               # SQLAlchemy models (Item, Allergen, MeatType, Category, Admin, AppSettings)
├── schemas.py               # Pydantic schemas
├── queries.py                # DB query functions
├── seed/
│   ├── insert_data.py         # Functions that insert data into the DB
│   ├── items.py                 # Real item+allergen data (gitignored, see below)
│   ├── item_meat.py               # Real item+meat data (gitignored, optional)
│   ├── allergens.py                # NVWA allergen reference data
│   └── meat_types.py                 # Meat type reference data
├── pdf_generator.py           # PDF export logic
└── static/
    └── icons/                # Allergen and meat type icons, served via FastAPI static files

alembic/
├── env.py                # Migration environment config, reads models + DATABASE_URL
└── versions/               # Migration history

alembic.ini                # Alembic top-level config
requirements.txt             # Backend dependencies (pip freeze output)
.env                          # Local environment variables (gitignored)
.env.example                   # Template for required environment variables
```

`main.py`, at the project root, only handles app setup, middleware, static files, rate limiter registration, startup seeding, and wiring the routers together via `app.include_router(...)` — no route logic lives there directly.

---

## 🗂️ Project Structure (frontend)

```
frontend/src/
├── components/
│   ├── Navbar.jsx        # Clickable brand/home link, PDF download, language switcher
│   ├── Footer.jsx          # Company name (from settings) + auto-updating year
│   ├── FilterBar.jsx        # Search box + allergen/meat type/category filter checkboxes
│   ├── Modal.jsx              # Reusable popup used throughout the admin area
│   ├── RequireAuth.jsx          # Route guard — redirects to /login if not authenticated
│   ├── AdminLayout.jsx            # Shared admin header/logout + <Outlet /> for nested admin pages
│   └── CodeLabelAdmin.jsx           # Reusable list/create/edit/delete UI for code+translation resources
│                                      (used for allergens, meat types, and categories)
├── pages/
│   ├── AllergensPage.jsx     # "/" — the item x allergen (+ meat type) matrix, with filtering
│   ├── LoginPage.jsx           # "/login" — admin login form
│   ├── AdminLandingPage.jsx      # "/admin" — links to each admin section
│   ├── AdminItemsPage.jsx          # "/admin/items" — item management (name, category, allergens, meats)
│   ├── AdminCategoriesPage.jsx       # "/admin/categories" — uses CodeLabelAdmin
│   ├── AdminAllergensPage.jsx          # "/admin/allergens" — uses CodeLabelAdmin
│   ├── AdminMeatTypesPage.jsx            # "/admin/meat-types" — uses CodeLabelAdmin
│   └── AdminSettingsPage.jsx               # "/admin/settings" — app-wide settings form
│   └── AdminAccountPage.jsx                  # "/admin/account" — change the admin's own password
├── styles/                   # CSS split by concern (base, navbar, matrix, filterbar, auth, admin, modal)
├── localization.jsx           # React Context: current language, translations, language switcher state
├── authContext.jsx              # React Context: JWT token, login/logout, token validation on load
├── api.js                         # Shared authenticated-fetch helper for admin requests
├── App.jsx                          # Assembles layout and defines routes (including nested admin routes)
└── main.jsx                           # App entry point, wraps App in BrowserRouter + providers

frontend/public/
└── robots.txt   # Disallows all crawlers from indexing any page (site isn't meant to be publicly searchable)
```

---

## 🧪 Example Data

The application automatically seeds:

### Allergens (simplified example)

* Gluten
* Milk
* Soy
* Mustard

### Categories

* Snacks
* Bakery

### Items

* **Frikandel** → gluten, soy, mustard, category: Snacks
* **Kroket** → gluten, milk, category: Snacks
* **Bread** → gluten, category: Bakery
* **Fishstick** → fish, category: Snacks

### Admin account

A single admin account is seeded on first startup, from `ADMIN_USERNAME`/`ADMIN_PASSWORD` in `.env`. Its password is stored as a bcrypt hash — the plaintext value from `.env` is never stored anywhere. Re-running the seed does not reset an existing admin's password.

---

## 📝 Logging & Audit Trail

The app uses Python's standard `logging` module, configured once at startup (timestamp, level, and module name on every line) instead of scattered `print()` statements.

* **Security events** — failed and successful login attempts are logged (`WARNING` / `INFO`), including the requester's IP, making it possible to spot repeated failed-login patterns
* **Audit trail** — every admin create/update/delete action (items, allergens, meat types, categories, settings) is logged under a separate `"audit"` logger, recording who did what to which resource
* **Unhandled errors** — any exception that isn't explicitly caught is logged with its full traceback server-side, while the client only ever receives a generic `"Internal server error"` message — full details never leak into an API response
* **Persistence** — logs are written to both the terminal and a rotating file at `logs/app.log` (capped at ~1MB, keeping the last 5 rotated files), so history survives after the terminal closes. The `logs/` folder is gitignored.

---

## 🔐 Authentication & Admin Access

The project has a single admin account (no multi-user roles) protecting all write operations.

* **Login** — `POST /auth/login` with a username/password, returns a JWT access token (1 hour expiry)
* **Protected routes** — every `POST`/`PUT`/`DELETE` endpoint requires a valid `Authorization: Bearer <token>` header
* **Public reads** — `GET` endpoints (items, allergens, meat types, categories, config) remain open, since the public matrix page needs them without anyone logging in
* **Password storage** — hashed with bcrypt via `passlib`, never stored or logged in plaintext
* **Rate limiting** — `POST /auth/login` is limited to 5 attempts per minute per IP address (via `slowapi`), to make brute-force password guessing impractical
* **Frontend session** — the JWT is stored in `localStorage` and validated against `GET /auth/me` on page load, so a stale or tampered token doesn't silently grant access to the admin UI. It's also checked on every subsequent request — if any authenticated call returns `401` (e.g. the token expired mid-session), the frontend immediately clears it and redirects to `/login`.
* **Changing your password** — from `/admin/account`, an admin can change their own password by confirming their current one. This immediately invalidates the current session and requires logging in again with the new password.

---

## 🚩 Settings

App-wide settings are stored in the database (a single-row `AppSettings` table), not in source code — this means they're editable from the admin area at `/admin/settings` without redeploying.

Current settings:

* **Meat tracking** — whether meat type data is tracked and shown at all. Off by default; when off, meat reference data still has its table but nothing gets seeded or displayed.
* **Company name** — shown in the site footer.
* **Site title (English / Dutch)** — the title shown in the navbar, per language.
* **Logo** — an optional image shown beside the site title in the navbar. Uploading replaces any existing logo; supports PNG, JPG, and SVG up to 2MB.
* **Default language** — which language (`nl`/`en`) the public matrix page loads in by default.

---

## 🔐 Environment Configuration

Configuration that varies between environments and secrets lives in a `.env` file, not hardcoded in the source code.

Copy the template to create your own local config:

```bash
cp .env.example .env
```

`.env.example`:
```
DATABASE_URL=sqlite:///product_management.db
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password-here
```

Generate a real `SECRET_KEY` (used to sign JWTs) rather than leaving the placeholder:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

By default, the project runs against a local SQLite file — no separate database server required. `DATABASE_URL` can be changed to point at a hosted PostgreSQL database instead for a more production-style setup; both are supported through the same variable, since SQLAlchemy abstracts over the underlying database engine.

`.env` is gitignored. `.env.example` is committed as a template with placeholder values only.

Uploaded vendor logos are saved to `src/product_management/static/logos/` and are also gitignored (with a `.gitkeep` placeholder so the empty folder itself stays tracked), since they're vendor-specific uploads rather than application code.

---

## 🧬 Database Migrations

Schema changes are managed with **Alembic**, rather than deleting and recreating the database file on every model change.

Workflow for any future schema change:

```bash
# 1. Edit models.py

# 2. Generate a migration describing the change
alembic revision --autogenerate -m "short description"

# 3. Review the generated file in alembic/versions/

# 4. Apply it
alembic upgrade head
```

For a fresh clone of this project, running `alembic upgrade head` once builds the full database schema from the committed migration history — no manual table creation needed.

---

## 🔁 Continuous Integration

Every push and pull request to `main` automatically runs a full pipeline via **GitHub Actions** (`.github/workflows/tests.yml`), in a clean environment separate from any local machine:

1. **Lint** — `ruff check .`
2. **Format check** — `ruff format --check .`
3. **Type check** — `mypy src/ main.py`
4. **Tests** — `pytest tests/ -v`

Each step must pass before the next runs, so the fastest, cheapest checks (lint, format) fail fast before the full test suite runs. The badge at the top of this README reflects the current status.

---

## 🚀 Running the Project

The backend and frontend run as two separate servers during development.

### 1. Backend setup

```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
```

Start the backend:

```bash
uvicorn main:app --reload
```

The API is now available at `http://localhost:8000`, with interactive docs (Swagger UI) at:

```
http://localhost:8000/docs
```

Note this is the **backend** port (`8000`) — the frontend dev server (`5173`, started below) doesn't have this route.

Endpoints are grouped into labeled sections (Items, Allergens, Meat Types, Categories, Authentication, Settings, Backup & Restore, Health) via OpenAPI tags, rather than one flat list.

### 2. Frontend setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev -- --host
```

The frontend is now available at `http://localhost:5173`.

Both servers must be running at the same time for the frontend to fetch data from the backend. CORS is configured on the backend to allow requests from `http://localhost:5173`.

### 3. Logging into the admin area

Go to `http://localhost:5173/login` and sign in with the `ADMIN_USERNAME`/`ADMIN_PASSWORD` values from your `.env` file.

---

## 🔍 Available Endpoints

**Public**
* `GET /items` – list items with their allergens and meat types. Supports `limit`/`offset` (pagination), `search`, `exclude_allergens` (repeatable), `meat_types` (repeatable), `categories` (repeatable). (A dedicated `/gluten-free` endpoint existed early on, before general filtering — removed once it became fully redundant with `?exclude_allergens=gluten`.)
* `GET /allergens` – list all known allergens
* `GET /meat-types` – list all known meat types (empty if meat tracking is disabled)
* `GET /categories` – list all categories
* `GET /items/pdf?language=nl|en` – generate a downloadable PDF file of the allergen matrix
* `GET /config` – current app settings
* `GET /health` – reports whether the API and database are reachable

**Authentication**
* `POST /auth/login` – authenticate, returns a JWT (rate limited: 5/minute per IP)
* `GET /auth/me` – returns the current admin's identity if the token is valid
* `PUT /auth/password` – change the current admin's password (requires the current password); invalidates the session, requiring a fresh login

**Admin-only (require a valid Bearer token)**
* `POST` / `PUT` / `DELETE` on `/items/{id}`, `/allergens/{id}`, `/meat-types/{id}`, `/categories/{id}`
* `PUT /config` – update app settings
* `POST /config/logo` – upload a vendor logo (PNG/JPG/SVG, max 2MB), replacing any existing one
* `DELETE /config/logo` – remove the current logo
* `GET /data/export` – export all business data (items, allergens, meat types, categories, settings) as JSON — excludes the admin account
* `POST /data/import` – **replace** all business data with the contents of an imported JSON export (destructive; the admin account is untouched)

---

## 🧭 Frontend Pages

* `/` – **Allergen Matrix** page. A filter bar above the content lets someone search by name and filter by allergen (exclude), meat type, and category, refetching live as filters change. On wider screens, a table with items down the left and allergens (with icons) — plus meat type columns when enabled — across a sticky header row, grouped visually by category. On narrower screens, the table becomes a card-per-item layout instead. Results are paginated (30 per page); changing any filter resets back to page 1.
* `/login` – Admin login form.
* `/admin` – Admin landing page, linking to each management section (Items, Settings, and grouped reference data: Categories, Allergens, Meat Types). Protected — redirects to `/login` if not authenticated.
* `/admin/items` – Create, edit, and delete items: name, category (dropdown), allergens and meat types (checkboxes). Invalid codes can't be submitted through this UI, but the backend still validates and reports warnings if bypassed via direct API access. Paginated (25 per page).
* `/admin/categories`, `/admin/allergens`, `/admin/meat-types` – Each uses the same reusable list/create/edit/delete UI, since all three share the same code + English/Dutch description shape.
* `/admin/settings` – Update company name, site title, logo, default language, and the meat tracking toggle. Requires confirmation before saving, since these affect the whole site.
* `/admin/account` – Change the admin's own password. Requires the current password, and confirming a new password twice client-side before submitting. On success, the session ends immediately and the admin must log in again.

`/admin/settings` also includes a **Backup & Restore** section: "Export all data" downloads a full JSON snapshot (items, allergens, meat types, categories, settings), and "Import data" accepts a previously exported file and **replaces** all current business data with its contents. Import is explicitly confirmed given it's destructive and irreversible; the admin account itself is untouched by either operation.

Each admin sub-page shows a "← Back" link beside its own title, returning to `/admin`; "Log out" stays persistently visible top-right across every admin page.

---

## 📚 What I Learned From This Project

* How to translate **legal/business requirements** into data models
* React fundamentals: components, props, state, effects, conditional rendering
* Connecting a React frontend to a FastAPI backend (CORS, fetch, serving static files)
* Structuring a growing codebase into clear, single-purpose modules, including splitting routes into FastAPI routers
* Client-side routing with React Router, including nested and protected routes
* Combining data from multiple API endpoints in the frontend to build a matrix view
* CSS Grid, sticky positioning, and media queries for responsive, dual (table/card) layouts
* React Context, for sharing state (language, auth) across components without prop drilling
* Database migrations with Alembic, and why they matter once a project has real data to preserve
* Building a reusable admin CRUD component shared across multiple resource types, instead of duplicating near-identical forms
* Practicing fixing real bugs that a static type checker (mypy) surfaced — a duplicate class definition silently overriding another, two unrelated classes sharing a name, and an unguarded optional attribute — rather than just running the tool
* Writing composable SQLAlchemy queries with multiple optional filters applied conditionally
* Testing an authenticated API with pytest fixtures, including handling stateful complications like rate limiter state leaking between tests
* Structured application logging: consistent formatting, appropriate severity levels, a separate audit-trail logger for admin actions, and logging full tracebacks server-side while returning generic error messages to clients

---

## 🤖 Learning React and Backend Security with AI

I'm learning React and practicing JavaScript as part of this project, and more recently used AI to explore backend security concepts (particularly the tradeoffs discussed in **Authentication & Admin Access** and **Backend Security Notes** below). I've used **Claude** as a learning tool — for help when I got stuck on something specific, for exploring security topics I hadn't worked with before, and for writing this documentation.

I see this as similar to using a tutorial, documentation, or a mentor: the AI helps me understand *why* something works the way it does, but the implementation decisions, debugging, and understanding are still mine to build. I'm noting this openly here since transparency about how I learn and build matters to me, especially in a portfolio project.

---

## 🛡️ Backend Security Notes

A few small, deliberate additions, plus known tradeoffs worth documenting honestly rather than leaving unstated:

**Response headers** — every response includes:
* `X-Content-Type-Options: nosniff` — prevents the browser from guessing a file's type differently than declared
* `X-Frame-Options: DENY` — prevents the site being loaded inside an `<iframe>` on another page (clickjacking protection)
* `Referrer-Policy: same-origin` — avoids leaking referrer URLs to external destinations

`Content-Security-Policy` and `Strict-Transport-Security` were deliberately left out for now — CSP needs careful tuning to avoid breaking the app's own scripts/styles, and HSTS only makes sense once this is served over HTTPS rather than local `http://localhost`. Both are worth adding at actual deployment time.

**Known, deliberate tradeoffs:**
* **JWT stored in `localStorage`, not an httpOnly cookie** — readable by JavaScript, which matters if the app ever had an XSS vulnerability. An httpOnly cookie avoids that specific risk but introduces its own (CSRF), needing separate protection. For a small, single-admin internal tool, `localStorage` is a reasonable choice; it would need revisiting for anything more sensitive or multi-user.
* **No token revocation** — JWTs are stateless: a token remains valid until it naturally expires (1 hour), even after logging out or changing password on another device. A proper fix (short-lived access tokens + server-side refresh tokens) roughly doubles the complexity of the auth system — reasonable to add later if this ever supports multiple admins, not necessary at the current scale.
* **No enforced password strength requirement** on `PUT /auth/password` — a known, currently-accepted gap.

**Logo upload validation** — uploaded files are checked beyond just their extension: PNG/JPEG are verified against their actual binary file signature ("magic bytes"), and SVG files are parsed as XML and rejected if they contain a `<script>` tag. This is a deliberately basic check, not a full SVG sanitizer — a sufficiently motivated attacker could still use other SVG-based vectors (e.g. `onload=` event handler attributes). Since logos are only ever rendered via `<img>` tags (which don't execute embedded scripts) and only a single trusted admin can upload them, this is a proportionate, not exhaustive, defense.

---

## 🔮 Future Improvements

Planned extensions include:

* PostgreSQL as a documented, tested alternative to SQLite for hosted deployments
* Docker (containerized deployment)

---

## 📦 Item Data Source

This project ships with sample item data for demo and development purposes.

By default, the application loads data from an internal sample dataset: `SAMPLE_ITEMS`, defined in `src/product_management/seed/insert_data.py`.

### Using real item data

If you want to use your own (real) item data, you can provide it via a file that is intentionally excluded from version control.

Create a file at:

```
src/product_management/seed/items.py
```

Define a variable called `items` with the same structure as `SAMPLE_ITEMS`:

```python
items = {
    "Example item": ["gluten", "milk"],
    "Another item": ["nuts"],
}
```

When present, the application will automatically load this data instead of the sample data. If the file is not found, the system safely falls back to the sample dataset.

**Note:** `src/product_management/seed/items.py` is listed in `.gitignore` to keep real business data out of version control.

### Using real meat type data (optional)

If **meat tracking** is enabled (see **Settings** above), you can similarly provide real per-item meat data via a file excluded from version control.

Create a file at:

```
src/product_management/seed/item_meat.py
```

Define a variable called `item_meat` with the same structure as the sample data:

```python
item_meat = {
    "Example item": ["pork", "beef"],
    "Another item": [],
}
```

If this file isn't present, the application falls back to a small internal sample dataset. `src/product_management/seed/item_meat.py` is also listed in `.gitignore`.

### Categories

Unlike items and meat assignments, categories are managed through the **admin area** (`/admin/categories`) rather than a seed file, since they're a proper database table that both an admin and the seeded sample items reference by key.

---

## 💬 Final Note

This project is part of my **personal learning journey and portfolio** and will continue to evolve over time.

This project is intentionally **practical**.

It represents how I approach development:

* Start from real requirements
* Model the domain carefully
* Prefer clarity over complexity
* Learn by building — including learning openly with the help of AI tools

Feedback and suggestions are always welcome.