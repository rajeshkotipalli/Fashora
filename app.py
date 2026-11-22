import os, re, json, sqlite3
from datetime import date
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort, jsonify
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
import data, chatbot

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",   # set COOKIE_SECURE=1 once the site is on https
    MAX_CONTENT_LENGTH=64 * 1024,                                    # forms/JSON are tiny; reject anything bigger
)
os.makedirs(app.instance_path, exist_ok=True)
DB = os.path.join(app.instance_path, "fashora.db")

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

with sqlite3.connect(DB) as c:
    c.executescript("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pw TEXT);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, user_id INTEGER, total INTEGER, items TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, name TEXT, email TEXT, body TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);""")
    if "phone" not in [r[1] for r in c.execute("PRAGMA table_info(users)")]:   # upgrade older databases in place
        c.execute("ALTER TABLE users ADD COLUMN phone TEXT")

PRODUCTS = {p["id"]: p for p in data.PRODUCTS}
POSTS = {b["slug"]: b for b in data.BLOGS}
ICONS = {
 "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
 "heart": '<path d="M12 20s-7-4.5-9-9a5 5 0 0 1 9-3 5 5 0 0 1 9 3c-2 4.5-9 9-9 9z"/>',
 "bag": '<path d="M5 8h14l-1 12H6zM9 8a3 3 0 0 1 6 0"/>',
 "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>', "back": '<path d="M19 12H5m6-6-6 6 6 6"/>',
 "trash": '<path d="M4 7h16M9 7V4h6v3m-8 0 1 13h8l1-13"/>',
 "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
 "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 15-5 16 0"/>',
 "hanger": '<path d="M12 8a2.5 2.5 0 1 0-2.5-2.5M12 8v2L2 17h20l-10-7"/>',
 "truck": '<path d="M2 6h11v10H2zM13 10h5l3 3v3h-8z"/>', "ret": '<path d="M4 12a8 8 0 1 0 3-6M4 4v5h5"/>',
 "glasses": '<circle cx="6.5" cy="14" r="3.5"/><circle cx="17.5" cy="14" r="3.5"/><path d="M10 14h4M3 14l1.5-6M21 14l-1.5-6"/>',
 "cap": '<path d="M4 15a8 8 0 0 1 16 0z"/><path d="M20 15c2 .3 3 1 3 2H9"/>',
 "watch": '<rect x="7" y="7" width="10" height="10" rx="3"/><path d="M9 7l1-4h4l1 4M9 17l1 4h4l1-4M12 10v2l1.5 1"/>',
 "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
 "star": '<path d="m12 3 3 6 6 1-4.5 4.5L18 21l-6-3-6 3 1.5-6.5L3 10l6-1z"/>',
 "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01"/>',
 "send": '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>'}

def money(n):
    s = str(int(n))
    if len(s) > 3: s = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", s[:-3]) + "," + s[-3:]
    return "₹" + s

def cart_items():
    out = []
    for i, x in enumerate(session.get("cart", [])):
        p = PRODUCTS.get(x["id"])
        if p: out.append({**x, "i": i, "p": p, "line": p["price"] * x["qty"]})
    return out

def _static_version():
    try: return str(int(max(os.path.getmtime(os.path.join(app.static_folder, f)) for f in ("css/style.css", "js/app.js", "js/chat.js"))))
    except OSError: return "1"
STATIC_V = _static_version()

@app.context_processor
def inject():
    def img(path): 
        ok = os.path.exists(os.path.join(app.static_folder, "images", path))
        return url_for("static", filename="images/" + path) if ok else url_for("static", filename="placeholder.svg")
    def icon(n, s=18, fill="none"):
        return Markup(f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="{fill}" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[n]}</svg>')
    return dict(static_v=STATIC_V, img=img, icon=icon, money=money, user=session.get("user"), wish=session.get("wish", []),
                cart_count=sum(x["qty"] for x in session.get("cart", [])), ep=request.endpoint, owner=data.OWNER, year=date.today().year)

def safe_next(u):
    """Only allow redirects back to this same site (blocks open-redirect links)."""
    if not u: return None
    p = urlparse(u)
    return u if (not p.netloc or p.netloc == request.host) and p.scheme in ("", "http", "https") else None

def back(): return redirect(safe_next(request.form.get("next")) or safe_next(request.referrer) or url_for("home"))

@app.route("/")
def home():
    slides = [s for s in data.HERO if os.path.exists(os.path.join(app.static_folder, "images", s))] or data.HERO[:1]
    n = request.args.get("slide", 0, type=int) % len(slides)
    featured = [PRODUCTS[i] for i in (1, 5, 3, 7)]
    return render_template("home.html", slides=slides, cur=n, featured=featured, acc=PRODUCTS[8], posts=data.BLOGS[:3])

@app.route("/collections")
def collections(): return render_template("collections.html", cols=data.COLLECTIONS)

@app.route("/new-arrivals")
def arrivals(): return render_template("arrivals.html", imgs=data.ARRIVALS)

@app.route("/shop")
def shop():
    cat, s = request.args.get("cat"), request.args.get("q", "").lower()
    items = [p for p in data.PRODUCTS if (not cat or p["cat"] == cat) and s in p["name"].lower()]
    if request.args.get("sort") == "new": items = items[::-1]
    title = next((c["name"] for c in data.COLLECTIONS if c["cat"] == cat), "Shop All")
    return render_template("shop.html", items=items, cat=cat, q=request.args.get("q", ""), cols=data.COLLECTIONS, title=title)

@app.route("/product/<int:pid>")
def product(pid):
    p = PRODUCTS.get(pid) or abort(404)
    return render_template("product.html", p=p, cur=request.args.get("img", 0, type=int) % len(p["images"]))

@app.post("/wishlist/toggle/<int:pid>")
def wish_toggle(pid):
    w = session.get("wish", [])
    w.remove(pid) if pid in w else w.append(pid)
    session["wish"] = w
    return back()

@app.route("/wishlist")
def wishlist(): return render_template("wishlist.html", items=[PRODUCTS[i] for i in session.get("wish", []) if i in PRODUCTS])

@app.post("/cart/add/<int:pid>")
def cart_add(pid):
    p = PRODUCTS.get(pid) or abort(404)
    size, color = request.form.get("size", p["sizes"][0]), request.form.get("color", p["colors"][0])
    qty = max(1, request.form.get("qty", 1, type=int)); c = session.get("cart", [])
    hit = next((x for x in c if x["id"] == pid and x["size"] == size and x["color"] == color), None)
    if hit: hit["qty"] += qty
    else: c.append(dict(id=pid, size=size, color=color, qty=qty))
    session["cart"] = c; flash("Added to cart")
    return back()

@app.route("/cart")
def cart():
    items = cart_items()
    return render_template("cart.html", items=items, sub=sum(i["line"] for i in items))

@app.post("/cart/update/<int:i>")
def cart_update(i):
    c = session.get("cart", [])
    if i < len(c):
        act = request.form.get("act")
        if act == "del": c.pop(i)
        else: c[i]["qty"] = max(1, c[i]["qty"] + (1 if act == "inc" else -1))
    session["cart"] = c
    return redirect(url_for("cart"))

@app.post("/cart/clear")
def cart_clear(): session["cart"] = []; return redirect(url_for("cart"))

@app.post("/checkout")
def checkout():
    items = cart_items()
    if not items: return redirect(url_for("cart"))
    db().execute("INSERT INTO orders(user_id,total,items) VALUES(?,?,?)", (session.get("uid"), sum(i["line"] for i in items),
        json.dumps([{k: i[k] for k in ("id", "size", "color", "qty")} for i in items])))
    db().commit(); session["cart"] = []
    return render_template("success.html")

@app.route("/about")
def about(): return render_template("about.html", pic=data.ABOUT_IMG)

@app.route("/blog")
def blog(): return render_template("blog.html", latest=data.BLOGS[0], posts=data.BLOGS[1:])

@app.route("/blog/<slug>")
def blog_post(slug):
    b = POSTS.get(slug) or abort(404)
    more = [x for x in data.BLOGS if x["slug"] != slug][:3]
    return render_template("blog_post.html", b=b, more=more, items=[PRODUCTS[i] for i in b["shop"] if i in PRODUCTS][:3])

@app.errorhandler(404)
def nf(_): return render_template("404.html"), 404

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.route("/login", methods=["GET", "POST"])
def login():
    mode = "register" if request.args.get("mode") == "register" else "login"
    err, form = None, request.form
    if request.method == "POST":
        email, pw = form.get("email", "").strip().lower(), form.get("password", "")
        name, phone = form.get("name", "").strip()[:60], re.sub(r"[\s\-()]", "", form.get("phone", "").strip())
        if not EMAIL_RE.match(email): err = "Please enter a valid email address."
        elif len(pw) < 6: err = "Password must be at least 6 characters."
        elif mode == "register":
            if not name: err = "Please enter your name."
            elif phone and not re.fullmatch(r"\+?\d{7,15}", phone): err = "Please enter a valid mobile number, or leave it empty."
            else:
                try:
                    cur = db().execute("INSERT INTO users(name,email,pw,phone) VALUES(?,?,?,?)", (name, email, generate_password_hash(pw), phone or None))
                    db().commit(); session.update(uid=cur.lastrowid, user=name); return redirect(url_for("home"))
                except sqlite3.IntegrityError: err = "That email is already registered. Please log in instead."
        else:
            u = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if u and check_password_hash(u["pw"], pw):
                session.update(uid=u["id"], user=u["name"]); return redirect(url_for("home"))
            err = "Wrong email or password."
    return render_template("login.html", mode=mode, err=err, pic=data.LOGIN_IMG, form=form)

@app.route("/logout")
def logout(): session.pop("uid", None); session.pop("user", None); return redirect(url_for("home"))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    sent = request.method == "POST"
    if sent:
        db().execute("INSERT INTO messages(name,email,body) VALUES(?,?,?)", (request.form.get("name", "")[:80], request.form.get("email", "")[:120], request.form.get("body", "")[:2000])); db().commit()
    return render_template("contact.html", sent=sent)

# ---------------------------------------------------------------- AI assistant (see chatbot.py)
@app.get("/api/chat/start")
def chat_start():
    ep, pid = request.args.get("ep", "")[:30], request.args.get("pid", "")
    return jsonify(greeting=chatbot.greeting(ep, int(pid) if pid.isdigit() else None), suggestions=chatbot.suggestions(ep, 4))

@app.post("/api/chat")
def chat_api():
    body = request.get_json(silent=True) or {}
    msg = str(body.get("message", "")).strip()
    if not msg: return jsonify(error="Please type a question."), 400
    return jsonify(chatbot.answer(msg, str(body.get("ep", ""))[:30], body.get("pid")))

@app.after_request
def headers(r):
    r.headers.setdefault("X-Content-Type-Options", "nosniff")
    r.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if request.path.startswith("/api/"): r.headers["Cache-Control"] = "no-store"
    elif request.path.startswith("/static/"):   # css/js are versioned with ?v= so they can cache for long; images for an hour
        r.headers["Cache-Control"] = "public, max-age=2592000" if request.path.endswith((".css", ".js")) else "public, max-age=3600"
    return r

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
