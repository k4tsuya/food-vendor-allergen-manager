# Snack Bar Product & Allergen Management

## 📌 Project Overview

This project started from a **real, practical need** at my current **part-time job** in a snackbar in the Netherlands.

As a food business, we are legally required to:

* Maintain a clear and correct **allergen list**
* Be able to tell customers **which allergens are present in which items**
* Follow EU / NVWA (Nederlandse Voedsel- en Warenautoriteit) food allergen regulations

Managing this information manually quickly became error‑prone and time‑consuming. This project is my attempt to **solve that real-world problem with software**, while at the same time **learning and exploring new backend and frontend technologies**.

The project was originally built around "products," but has since been generalized to **"items"** — a deliberate step toward making this usable by any food vendor (bakery, restaurant, butcher, etc.), not just a snackbar. See **Feature Flags** below for how vendor-specific terminology is configured.

---

## 🚧 Project Status

This project is **actively under development** and is being built step by step as a learning project.

It is intended to become part of my **developer portfolio**, showcasing how I approach real-world backend problems, data modeling, frontend development, and new technologies.

---

## 🎯 Goals of This Project

* Model food allergens **correctly and realistically**
* Link allergens to items in a flexible way
* Create a clean and understandable backend foundation
* Build a working, presentable frontend to consume that backend
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

The same pattern (a dedicated reference table + many‑to‑many relationship) is reused for **meat types** — an optional feature for tracking which meats (pork, beef, chicken, turkey, horse, fish, lamb) are present in an item. See **Feature Flags** below.

---

## 🧱 Tech Stack

I intentionally chose this tech stack to **learn and explore different tools** beyond what I already knew.

**Backend**
* **Python 3.13**
* **FastAPI** – modern, fast backend framework
* **SQLAlchemy 2.0** – ORM with explicit, type‑safe models
* **SQLite** – local database for development (see **Database & Environment Configuration** for other options)
* **Alembic** – database schema migrations
* **Pydantic** – data validation and API schemas
* **pytest** – automated testing, with an isolated in-memory test database

**Frontend**
* **React** – component-based UI library
* **Vite** – frontend build tool and dev server
* **React Router** – client-side routing setup

Although I have previous experience with **Django + DRF**, this project focuses on:

* Understanding lower‑level ORM concepts
* Explicit database modeling
* Clear separation between models, schemas, and application logic
* Learning frontend development from the ground up with React

---

## 🗂️ Project Structure (backend)

```
src/product_management/
├── core/
│   ├── database.py       # DB engine/session setup + get_db dependency, reads DATABASE_URL from .env
│   └── config.py           # Feature flags and vendor config (ENABLE_MEAT_TRACKING, ITEM_LABEL)
├── routers/
│   ├── items.py             # /items, /gluten-free, /items/pdf routes
│   ├── allergens.py          # /allergens route
│   ├── health.py              # /health route
│   └── config.py                # /config route, exposes vendor label config to the frontend
├── models.py               # SQLAlchemy models (Item, Allergen, MeatType)
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
    └── icons/                # Allergen icons, served via FastAPI static files

alembic/
├── env.py                # Migration environment config, reads models + DATABASE_URL
└── versions/               # Migration history

alembic.ini                # Alembic top-level config
requirements.txt             # Backend dependencies (pip freeze output)
.env                          # Local environment variables (gitignored)
.env.example                   # Template for required environment variables
```

`main.py`, at the project root, only handles app setup, middleware, static files, startup seeding, and wiring the routers together via `app.include_router(...)` — no route logic lives there directly.

---

## 🗂️ Project Structure (frontend)

```
frontend/src/
├── components/
│   ├── Navbar.jsx        # Top navigation bar: PDF download link + language switcher
│   └── Footer.jsx          # Page footer
├── pages/
│   └── AllergensPage.jsx    # "/" — the item x allergen matrix view, plus legend
├── localization.jsx           # React Context: current language, translations, and the language switcher state
├── App.jsx                     # Assembles layout and defines routes
├── App.css                      # App-wide styling
└── main.jsx                      # App entry point, wraps App in BrowserRouter + LanguageProvider
```

---

## 🧪 Example Data

The application automatically seeds:

### Allergens (simplified example)

* Gluten
* Milk
* Soy
* Mustard

### Items

* **Frikandel** → gluten, soy, mustard
* **Kroket** → gluten, milk
* **Bread** → gluten
* **Fishstick** → fish

This data is inserted on application startup and is safe to run multiple times.

---

## 🚩 Feature Flags

Some features and terminology are configurable, since not every food vendor using this project needs the same things.

Configuration lives in `src/product_management/core/config.py`:

```python
ENABLE_MEAT_TRACKING = False  # Set to True to enable meat tracking features

ITEM_LABEL = {
    "en": "Item",
    "nl": "Item",
}
```

**Meat tracking** links items to the meat types they contain, using the same many‑to‑many pattern as allergens. It's `False` by default — when disabled, meat reference data is never seeded and no meat types get assigned to items, but the underlying database tables still exist (created for every model regardless of the flag).

**Item label** controls the terminology shown in the matrix header and the exported PDF — e.g. a bakery could set this to `"Product"`, or a restaurant to `{"en": "Dish", "nl": "Gerecht"}`. This value is the single source of truth: it's exposed via the `/config` endpoint, and both the frontend and the PDF generator fetch/use it from there, so the two can never drift out of sync with each other.

---

## 🔐 Database & Environment Configuration

Configuration that varies between environments (currently just the database connection) lives in a `.env` file, not hardcoded in the source code.

Copy the template to create your own local config:

```bash
cp .env.example .env
```

`.env.example`:
```
DATABASE_URL=sqlite:///product_management.db
```

By default, the project runs against a local SQLite file — no separate database server required, good for local development or a small single-machine deployment. `DATABASE_URL` can be changed to point at a hosted PostgreSQL database instead for a more production-style setup; both are supported through the same `DATABASE_URL` value, since SQLAlchemy abstracts over the underlying database engine.

`.env` is gitignored, since it's meant to hold local/real configuration. `.env.example` is committed as a template.

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

## 🚀 Running the Project

The backend and frontend run as two separate servers during development.

### 1. Backend setup

```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
```

Set the preferred **item label** and enable/disable **meat tracking** in `src/product_management/core/config.py` if desired (see **Feature Flags** above).

Start the backend:

```bash
uvicorn main:app --reload
```

The API is now available at `http://localhost:8000`, with interactive docs at:

```
http://localhost:8000/docs
```

### 2. Frontend setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev -- --host
```

The frontend is now available at `http://localhost:5173`.

Both servers must be running at the same time for the frontend to fetch data from the backend. CORS is configured on the backend to allow requests from `http://localhost:5173`.

---

## 🔍 Available Endpoints

* `GET /items` – list items with their allergens (paginated via `limit`/`offset`)
* `GET /gluten-free` – list items with no gluten allergen (paginated)
* `GET /allergens` – list all known allergens
* `GET /items/pdf?language=nl|en` – generate a downloadable PDF file of the allergen matrix
* `GET /health` – reports whether the API and database are reachable

---

## 🧭 Frontend Pages

* `/` – **Allergen Matrix** page, a table with items listed down the left and allergens (with icons) across a sticky header row, marking which items contain which allergens. Below the table sits a legend explaining the marker, plus a labeled key listing every allergen by name and icon. The item column header, and the equivalent PDF header, both reflect the configured **item label** for the current language.
* **Language switcher** — a button in the navbar toggles between Dutch and English at runtime, updating all translated text, allergen names, and the item label immediately.
* **Download PDF** – a navbar link that triggers the backend's `/items/pdf` endpoint, downloading the allergen matrix in the currently selected language.

A dedicated item list page was considered but removed in favor of the matrix view, since it already conveys the same information (item names + their allergens) more directly.

---

## 📚 What I Learned From This Project

* How to translate **legal/business requirements** into data models
* React fundamentals: components, props, state, effects, conditional rendering
* Connecting a React frontend to a FastAPI backend (CORS, fetch, serving static files)
* Structuring a growing codebase into clear, single-purpose modules, including splitting routes into FastAPI routers
* Client-side routing with React Router, and structuring an app into pages vs. reusable components
* Combining data from multiple API endpoints in the frontend (items + allergens) to build a matrix view
* CSS Grid and sticky positioning for responsive, scrollable layouts
* React Context, for sharing state (like the current language) across components without prop drilling
* Designing a single backend source of truth for configuration shared between a frontend and a generated PDF
* Database migrations with Alembic, and why they matter once a project has real data to preserve
* Managing environment-specific configuration (`.env`) instead of hardcoding values

---

## 🤖 Learning React with AI

I'm learning React as part of this project, and I've been using **Claude** as a learning tool throughout that process — asking it to explain concepts step by step (state, props, `.map()`, conditional rendering, etc.), review and refactor code, and help debug issues as they come up.

I see this as similar to using a tutorial, documentation, or a mentor: the AI helps me understand *why* something works the way it does, but the implementation decisions, debugging, and understanding are still mine to build. I'm noting this openly here since transparency about how I learn and build matters to me, especially in a portfolio project.

---

## 🔮 Future Improvements

Planned extensions include:

* `POST` / `PUT` / `DELETE` endpoints for items, allergens, and meat types
* An authenticated Admin/Manager area in the frontend for managing a vendor's own data
* A "clean start" flow, letting a new vendor populate their own data from the UI instead of editing seed files
* Support for **"may contain traces of"** allergens
* Search / filter functionality on the item matrix
* Wiring meat type data into the PDF export and the frontend matrix (currently tracked in the database, but not yet displayed)
* PostgreSQL as a documented, tested alternative to SQLite for hosted deployments

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

This approach allows:

* Running the project out-of-the-box
* Keeping real business data private
* Avoiding configuration or environment variables for simple setups

**Note:** `src/product_management/seed/items.py` is listed in `.gitignore` to keep real business data out of version control.

### Using real meat type data (optional)

If **meat tracking** is enabled (see **Feature Flags** above), you can similarly provide real per-item meat data via a file excluded from version control.

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