# 👗 Fashora

**Premium fashion for men, women, kids and accessories** – a full-stack e-commerce web app built with **Python (Flask)**, Jinja2 templates and SQLite.

🔗 **Live:** [rajeshkotipalli.pythonanywhere.com](https://rajeshkotipalli.pythonanywhere.com/)

---

## 📌 About

Fashora is a complete online fashion store: customers can browse collections, search and filter products, pick size and colour, save favourites to a wishlist, add items to a cart, create an account and place an order. It also has a style blog, a contact form and a built-in chat assistant that answers common shopping questions.

It is built with only Flask and the Python standard library on the backend and plain HTML, CSS and JavaScript on the frontend – no heavy frameworks.

---

## ✨ Features

**Shopping**
- Home page with hero slider, *Fresh Picks*, *Finish the Look* (caps, sunglasses, watches) and latest blog posts
- Collections: Men's Fashion, Women's Fashion, Kids Wear, Accessories, plus a New Arrivals page
- Shop page with category filter, search and sorting
- Product page with image gallery, colour and size selection, quantity, price vs MRP and **% OFF**, ratings and reviews
- **Wishlist** (heart button on every product)
- **Cart** – add, increase / decrease quantity, remove, clear
- **Checkout** – saves the order (with items and total) to the database and shows a success page

**Accounts**
- Register and log in with email and password (name, optional mobile number)
- Input validation and clear error messages (invalid email, short password, duplicate email, wrong credentials)
- Passwords stored as **salted hashes**, never as plain text

**Content and support**
- Style **blog** with full article pages (6 posts)
- **Contact form** – messages are saved to the database
- **Fashora Assistant** – chat widget on every page: a rule-based FAQ agent (no API key, no cost, same standard answers every time) that also reads live prices, sizes and categories from the product data and suggests questions based on the page you are on
- Custom **404** page

**Experience**
- Instant page changes without a full reload (`fetch` + History API); the chat conversation survives page changes
- Fully **responsive**: phones (360px and up, Android and iOS), tablets (portrait and landscape), laptops and large monitors; 44px touch targets, 16px inputs on phones (no iOS zoom-on-focus) and safe-area handling for notches

---

## 🛠️ Tech stack

| Layer | Technology |
| --- | --- |
| Language | Python 3 |
| Backend framework | **Flask 3** |
| Templates | **Jinja2** (shared `base.html`, reusable macros) |
| Database | **SQLite** (`users`, `orders`, `messages` tables) |
| Auth | Flask sessions (signed cookies) + Werkzeug password hashing |
| Server | **Gunicorn** (`Procfile` included) |
| Frontend | HTML5, CSS3 (Flexbox, Grid, `clamp()`, animations, media queries), vanilla JavaScript |
| Fonts | Google Fonts – Inter, Poppins, Playfair Display, Caveat |
| Hosting | PythonAnywhere (also works on Render, Railway, Heroku-style hosts or any VPS) |

---

## 🔒 Security basics

- Hashed passwords (`generate_password_hash` / `check_password_hash`)
- Session cookies are `HttpOnly` and `SameSite=Lax`; set `COOKIE_SECURE=1` once the site runs on HTTPS
- `SECRET_KEY` read from an environment variable
- Request size limit (64 KB) – forms and JSON are tiny, anything bigger is rejected
- Security headers (`X-Content-Type-Options`, `Referrer-Policy`) and sensible cache rules for static files and API responses
- Parameterised SQL queries throughout

---

## 📂 Project structure

```
fashora_python/
├── app.py              # Flask app: routes, sessions, database, headers
├── data.py             # products, collections, blog posts, owner details
├── chatbot.py          # rule-based Fashora Assistant (FAQ knowledge base)
├── requirements.txt    # flask, gunicorn
├── Procfile            # gunicorn start command
├── instance/
│   └── fashora.db      # SQLite database (created automatically)
├── static/
│   ├── css/style.css   # all styles + responsive layer
│   ├── js/app.js       # instant navigation, forms
│   ├── js/chat.js      # chat widget
│   └── images/         # hero, products, blog, about, login photos
└── templates/          # base, home, shop, product, cart, wishlist,
                        # login, blog, blog_post, contact, about,
                        # collections, arrivals, success, 404
```

---

## 🚀 Run locally

```bash
# 1. clone the repository
git clone https://github.com/RajeshKotipalli/fashora.git
cd fashora

# 2. (optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. run
python app.py
```

Open **http://127.0.0.1:5000**

---

## 🌐 Deploy

**PythonAnywhere**
1. Upload the project and create a virtualenv with `pip install -r requirements.txt`.
2. In the *Web* tab, create a Flask app and point the WSGI file to it:
   ```python
   import sys
   sys.path.insert(0, "/home/<username>/fashora_python")
   import os
   os.environ["SECRET_KEY"] = "<long random string>"
   from app import app as application
   ```
3. Set the static files mapping: URL `/static/` → `/home/<username>/fashora_python/static`.
4. Click **Reload**.

**Render / Railway / Heroku-style hosts**
- Start command: `gunicorn app:app --workers 2 --threads 4` (already in `Procfile`)
- Environment variables: `SECRET_KEY=<long random string>` (**required**), `COOKIE_SECURE=1` (after HTTPS is on)
- Health check: `GET /`

> **Database note:** SQLite lives in `instance/fashora.db`. On hosts with a temporary disk it is wiped on every deploy or restart, so attach a persistent disk mounted at `instance/` or move to a hosted database before going live.

---

## ✏️ Customise (all content lives in `data.py`)

| What | Where |
| --- | --- |
| Your name, phone, email (footer, contact page, chat) | `OWNER` at the bottom of `data.py` |
| Products, prices, MRP, sizes, colours | `PRODUCTS` (each colour dot can switch the photo with `cimg`) |
| Blog posts | `BLOGS` (newest first; each opens at `/blog/<slug>`) |
| Product photos | `static/images/products/<n>-1.jpg … <n>-4.jpg` |
| Hero slides | `static/images/hero/hero-1.jpg`, `hero-2.jpg`, `hero-3.jpg` (missing ones are skipped) |
| Chat answers and suggested questions | `chatbot.py` → `kb()`, `PAGE_POOL`, `GENERIC_POOL` |
| Free-delivery amount used by the chat | `FREE_SHIPPING` in `chatbot.py` (home page text is in `templates/home.html`) |

Chat self-test (checks that every suggested question gets a real answer):

```bash
python chatbot.py
```

---

## ⚠️ Current limitations

- Checkout **records the order but has no payment gateway** yet.
- The chat assistant is **rule-based**, not AI-powered; for things like order tracking or password reset it points customers to the contact details.
- The catalogue is a small **sample set** (8 products) kept in `data.py`.

## 🧭 Roadmap

- [ ] Online payments (Razorpay / Stripe)
- [ ] Order history page and order tracking
- [ ] Admin dashboard to manage products and orders
- [ ] Password reset by email
- [ ] CSRF protection on forms
- [ ] Move the product catalogue from `data.py` to the database

---

## 👤 Author

**K Rajesh**
GitHub: [RajeshKotipalli](https://github.com/RajeshKotipalli) · LinkedIn: [rajesh-kotipalli](https://linkedin.com/in/rajesh-kotipalli-b82602288) · Portfolio: [kotipallirajesh.netlify.app](https://kotipallirajesh.netlify.app)

---

_Product names, prices and blog articles are sample content for demonstration._
