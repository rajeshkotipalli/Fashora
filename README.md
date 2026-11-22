# Fashora (Python / Flask)

Made by **K Rajesh** | 93466674777 | k94586034@gmail.com

Stack: Flask + Jinja2 templates + SQLite (users, orders, messages are saved in `instance/fashora.db`).

## Run locally
    pip install -r requirements.txt
    python app.py        # open http://127.0.0.1:5000

## Deploy (Render / Railway / Heroku-style hosts / any VPS)
    Start command:   gunicorn app:app --workers 2 --threads 4     (already in `Procfile`)
    Environment:     SECRET_KEY=<long random string>      <- REQUIRED, never leave the default
                     COOKIE_SECURE=1                      <- set once the site is served over https
    Health check:    GET /
**Database note:** SQLite lives in `instance/fashora.db`. On hosts with a temporary disk (Render free, Heroku) it is wiped on every
deploy/restart, so attach a persistent disk/volume mounted at `instance/` (or move to a hosted database before going live).

## Works on every screen
Phones (360px and up, Android + iOS), tablets (portrait + landscape), laptops and large monitors.
All breakpoints are in one block at the bottom of `static/css/style.css` ("RESPONSIVE LAYER").
Inputs are 16px on phones (stops iOS zoom-on-focus), buttons are 44px touch targets, safe-area insets handle notches.

## Fashora Assistant (chat widget, bottom-right)
Rule-based FAQ agent: no API key, no cost, same standard answers every time. It also reads live prices / sizes / categories from `data.py`.
- Edit answers and keywords: `chatbot.py` -> `kb()`
- Edit the suggested questions (they change per page and are shuffled each time the chat opens): `chatbot.py` -> `PAGE_POOL` / `GENERIC_POOL`
- Self-test (checks every suggested question gets a real answer):  `python chatbot.py`
- Things the bot says it can't do online yet (order tracking, password reset, payment options) point customers to your phone/email.
  When you add those features, update the matching entries in `kb()`.

## Edit content (all in data.py)
- Your name / phone / email (footer + Contact page + chat): `OWNER` at the bottom of data.py
- Products, prices, colours: `PRODUCTS`  (each colour dot can switch the photo: `cimg` = photo number for that colour)
- Blog posts: `BLOGS` (newest first). Each post opens as a full article at /blog/<slug>
- Images: static/images/<folder>/  (product photos are products/<name>-1..4.jpg)
- Hero slides: hero/hero-1.jpg, hero-2.jpg, hero-3.jpg (missing ones are skipped)
- Login photo: `static/images/login/login.jpg` (4:5 portrait, ~415x520 or larger works best)
- Free-delivery amount used by the chat: `FREE_SHIPPING` in chatbot.py (the home page text is in templates/home.html)
