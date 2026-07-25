# Snack Bar Product & Allergen Management

## 📌 Project Overview

This project started from a **real, practical need** at my current **part-time job** in a snackbar in the Netherlands.

As a food business, we are legally required to:

* Maintain a clear and correct **allergen list**
* Be able to tell customers **which allergens are present in which products**
* Follow EU / NVWA (Nederlandse Voedsel- en Warenautoriteit) food allergen regulations

Managing this information manually quickly became error‑prone and time‑consuming. This project is my attempt to **solve that real-world problem with software**, while at the same time **learning and exploring new backend and frontend technologies**.

---

## 🚧 Project Status

This project is **actively under development** and is being built step by step as a learning project.

It is intended to become part of my **developer portfolio**, showcasing how I approach real-world backend problems, data modeling, frontend development, and new technologies.

---

## 🎯 Goals of This Project

* Model food allergens **correctly and realistically**
* Link allergens to products in a flexible way
* Create a clean and understandable backend foundation
* Build a working, presentable frontend to consume that backend
* Learn and practice technologies I have not used deeply before
* Build a meaningful portfolio project based on real business needs

---

## 🧠 Domain Modeling

A key design decision in this project is **how allergens are modeled**.

* Allergens are **not boolean fields** on a product
* Allergens are a **fixed, regulated list** (EU / NVWA)
* Products can contain **multiple allergens**
* One allergen can apply to **multiple products**

Because of this, the project uses a **many‑to‑many relationship** between:

* `Product`
* `Allergen`

This approach:

* Matches real‑world legislation
* Avoids fragile database schemas
* Makes the system easy to extend in the future (e.g. "may contain traces of")

The same pattern (a dedicated reference table + many‑to‑many relationship) is reused for **meat types** — an optional feature for tracking which meats (pork, beef, chicken, etc.) are present in a product. See **Feature Flags** below.

---

## 🧱 Tech Stack

I intentionally chose this tech stack to **learn and explore different tools** beyond what I already knew.

**Backend**
* **Python 3.13**
* **FastAPI** – modern, fast backend framework
* **SQLAlchemy 2.0** – ORM with explicit, type‑safe models
* **SQLite** – simple local database for development
* **Pydantic** – data validation and API schemas

**Frontend**
* **React** – component-based UI library
* **Vite** – frontend build tool and dev server
* **React Router** – client-side routing setup (single route: the allergen matrix)

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
│   ├── database.py       # DB engine/session setup + get_db dependency
│   └── config.py           # Feature flags (e.g. ENABLE_MEAT_TRACKING)
├── routers/
│   ├── products.py         # /products, /gluten-free, /products/pdf routes
│   ├── allergens.py         # /allergens route
│   └── health.py             # /health route
├── models.py               # SQLAlchemy models
├── schemas.py               # Pydantic schemas
├── queries.py                # DB query functions
├── seed/
│   ├── insert_data.py         # Functions that insert data into the DB
│   ├── products.py             # Real product+allergen data (gitignored, see below)
│   ├── product_meat.py          # Real product+meat data (gitignored, optional)
│   ├── allergens.py              # NVWA allergen reference data
│   └── meat_types.py              # Meat type reference data
├── pdf_generator.py           # PDF export logic
└── static/
    └── icons/                # Allergen icons, served via FastAPI static files
```

`main.py`, at the project root, only handles app setup, middleware, static files, startup seeding, and wiring the routers together via `app.include_router(...)` — no route logic lives there directly.

---

## 🗂️ Project Structure (frontend)

```
frontend/src/
├── components/
│   ├── Navbar.jsx        # Top navigation bar with Allergens link + PDF download
│   └── Footer.jsx          # Page footer
├── pages/
│   └── AllergensPage.jsx    # "/" — allergen x product matrix view, plus legend
├── localization.js           # Central language setting and translated text
├── App.jsx                    # Assembles layout and defines routes
├── App.css                     # App-wide styling
└── main.jsx                     # App entry point, wraps App in BrowserRouter
```

---

## 🧪 Example Data

The application automatically seeds:

### Allergens (simplified example)

* Gluten
* Milk
* Soy
* Mustard

### Products

* **Frikandel** → gluten, soy, mustard
* **Kroket** → gluten, milk
* **Bread** → gluten
* **Fishstick** → fish

This data is inserted on application startup and is safe to run multiple times.

---

## 🚩 Feature Flags

Some features are optional, since not every business using this project needs them.

Feature flags live in `src/product_management/core/config.py`:

```python
ENABLE_MEAT_TRACKING = False  # Set to True to enable meat tracking features
```

**Meat tracking** links products to the meat types they contain (pork, beef, chicken, turkey, horse, fish, lamb), using the same many‑to‑many pattern as allergens. It's `False` by default — when disabled, meat reference data is never seeded and no meat types get assigned to products, but the underlying database tables still exist (created for every model regardless of the flag). Setting this to `True` and restarting the app (with a fresh database, see below) enables the feature.

---

## 🚀 Running the Project

The backend and frontend run as two separate servers during development.

### 1. Backend setup

```bash
pip install -r requirements.txt
```

Set the preferred language for the generated PDF file via the `language` variable in the `download_products_pdf()` function (`main.py`), set to `'en'` or `'nl'`.

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

* `GET /products` – list products with their allergens
* `GET /gluten-free` – list products with no gluten allergen
* `GET /allergens` – list all known allergens
* `GET /products/pdf` – generate a downloadable PDF file
* `GET /static/icons/{filename}` – serves allergen icon images
* `GET /health` – reports whether the API and database are reachable

---

## 🧭 Frontend Pages

* `/` – **Allergen Matrix** page, a table with products listed down the left and allergens (with icons) across a sticky header row, marking which products contain which allergens. Below the table sits a legend explaining the marker, plus a labeled key listing every allergen by name and icon.
* **Download PDF** – a navbar link that triggers the backend's `/products/pdf` endpoint directly, downloading the same allergen matrix as a PDF file

The dedicated product list page was removed in favor of the matrix view, since it already conveys the same information (product names + their allergens) more directly.

---

## 📚 What I Learned From This Project

* How to translate **legal/business requirements** into data models
* React fundamentals: components, props, state, effects, conditional rendering
* Connecting a React frontend to a FastAPI backend (CORS, fetch, serving static files)
* Structuring a growing codebase into clear, single-purpose modules
* Client-side routing with React Router, and structuring an app into pages vs. reusable components
* Combining data from multiple API endpoints in the frontend (products + allergens) to build a matrix view
* CSS Grid and sticky positioning for responsive, scrollable layouts

---

## 🤖 Learning React with AI

I'm learning React as part of this project, and I've been using **Claude** as a learning tool throughout that process — asking it to explain concepts step by step (state, props, `.map()`, conditional rendering, etc.), review and refactor code, and help debug issues as they come up.

I see this as similar to using a tutorial, documentation, or a mentor: the AI helps me understand *why* something works the way it does, but the implementation decisions, debugging, and understanding are still mine to build. I'm noting this openly here since transparency about how I learn and build matters to me, especially in a portfolio project.

---

## 🔮 Future Improvements

Planned extensions include:

* Product creation via API (`POST /products`)
* Support for **"may contain traces of"** allergens
* Search / filter functionality on the products page
* Runtime language switching (Dutch/English toggle) instead of a fixed setting in `localization.js`

---

## 📦 Product Data Source

This project ships with sample product data for demo and development purposes.

By default, the application loads data from an internal sample dataset: `SAMPLE_PRODUCTS`, defined in `src/product_management/seed/insert_data.py`.

### Using real product data

If you want to use your own (real) product data, you can provide it via a file that is intentionally excluded from version control.

Create a file at:

```
src/product_management/seed/products.py
```

Define a variable called `products` with the same structure as `SAMPLE_PRODUCTS`:

```python
products = {
    "Example product": ["gluten", "milk"],
    "Another product": ["nuts"],
}
```

When present, the application will automatically load this data instead of the sample data. If the file is not found, the system safely falls back to the sample dataset.

This approach allows:

* Running the project out-of-the-box
* Keeping real business data private
* Avoiding configuration or environment variables for simple setups

**Note:** `src/product_management/seed/products.py` is listed in `.gitignore` to keep real business data out of version control.

### Using real meat type data (optional)

If **meat tracking** is enabled (see **Feature Flags** above), you can similarly provide real per-product meat data via a file excluded from version control.

Create a file at:

```
src/product_management/seed/product_meat.py
```

Define a variable called `product_meat` with the same structure as the sample data:

```python
product_meat = {
    "Example product": ["pork", "beef"],
    "Another product": [],
}
```

If this file isn't present, the application falls back to a small internal sample dataset. `src/product_management/seed/product_meat.py` is also listed in `.gitignore`.

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