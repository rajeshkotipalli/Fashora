"""Fashora Assistant - a rule-based FAQ agent (no API key, no cost, same answers every time).

HOW TO EDIT
  * Standard answers ........ the KB list below (keywords -> answer).
  * Suggested questions ..... PAGE_POOL / GENERIC_POOL (every question there must be answerable by the KB;
                              run `python chatbot.py` to self-test).
  * Prices, sizes, categories are read live from data.py, so they never go out of date.
"""
import random
import re

from flask import url_for

import data

FREE_SHIPPING = 999  # keep in sync with the "Free delivery above Rs 999" text on the home page
OWNER = data.OWNER
CAT_LABEL = {c["cat"]: c["name"] for c in data.COLLECTIONS}
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL", "4Y", "6Y", "8Y", "10Y", "Free"]
PRODUCTS = {p["id"]: p for p in data.PRODUCTS}


# ------------------------------------------------------------------ helpers
def money(n):
    s = str(int(n))
    if len(s) > 3:
        s = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", s[:-3]) + "," + s[-3:]
    return "\u20b9" + s


def norm(text):
    t = text.lower().replace("t-shirt", "tshirt").replace("t shirt", "tshirt").replace("sun glasses", "sunglasses")
    t = re.sub(r"[^a-z0-9\u20b9 ]+", " ", t)
    return " " + re.sub(r"\s+", " ", t).strip() + " "


def tokens(text):
    out = set()
    for w in text.split():
        out.add(w)
        if len(w) > 3 and w.endswith("s"):
            out.add(w[:-1])  # naive plural -> singular
    return out


def link(key, label=None, **kw):
    """Lazy link spec - turned into a real URL per request by resolve() (url_for needs an app context)."""
    return {"key": key, "label": label, "kw": kw}


def resolve(spec):
    key, kw = spec["key"], spec["kw"]
    simple = {"shop": "Shop all", "cart": "Open cart", "contact": "Contact us", "login": "Login", "wishlist": "My wishlist",
              "blog": "Read the blog", "about": "About Fashora", "collections": "Collections"}
    if key in simple:
        return {"label": spec["label"] or simple[key], "url": url_for(key)}
    if key == "register":
        return {"label": spec["label"] or "Create account", "url": url_for("login", mode="register")}
    if key == "cat":
        return {"label": spec["label"] or kw.get("name", "Browse"), "url": url_for("shop", cat=kw["cat"])}
    if key == "product":
        return {"label": spec["label"] or kw.get("name", "View"), "url": url_for("product", pid=kw["pid"])}
    raise KeyError(key)


def cat_sizes(cat):
    seen = []
    for p in data.PRODUCTS:
        if p["cat"] == cat:
            seen += [s for s in p["sizes"] if s not in seen]
    return sorted(seen, key=lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else 99)


def pct_off(p):
    return int(round(100 - p["price"] * 100 / p["mrp"]))


def product_line(p):
    return f"{p['name']} - {money(p['price'])} (MRP {money(p['mrp'])}, {pct_off(p)}% off) | rating {p['rating']}"


def product_detail(p):
    colours = len(p["colors"])
    return (f"{p['name']}\n"
            f"Price: {money(p['price'])}  (MRP {money(p['mrp'])}, {pct_off(p)}% off)\n"
            f"Sizes: {', '.join(p['sizes'])}\n"
            f"Colours: {colours} option{'s' if colours != 1 else ''} - tap the colour dots on the product page\n"
            f"Rating: {p['rating']} from {p['reviews']} reviews\n{p['desc']}")


# --- product keyword index, built from data.py (so new products work automatically)
_GENERIC = {"premium", "classic", "white", "black", "red", "cream", "grey", "gray", "summer", "kids", "set",
            "and", "oversized", "top", "the", "free"}
PRODUCT_WORDS = {}
for _p in data.PRODUCTS:
    words = set(re.findall(r"[a-z]+", (_p["name"] + " " + _p["sub"]).lower().replace("t-shirt", "tshirt")))
    for w in words - _GENERIC:
        PRODUCT_WORDS.setdefault(w, set()).add(_p["id"])
    if "sunglasses" in words:
        PRODUCT_WORDS.setdefault("sunglass", set()).add(_p["id"])

CAT_WORDS = {"men": "men", "mens": "men", "man": "men", "male": "men", "boys": "men", "women": "women", "womens": "women",
             "woman": "women", "ladies": "women", "girls": "women", "female": "women", "kids": "kids", "kid": "kids",
             "child": "kids", "children": "kids", "baby": "kids", "accessories": "accessories", "accessory": "accessories",
             "watch": "accessories", "watches": "accessories"}
CONTEXT_WORDS = {"price", "cost", "size", "color", "colour", "rating", "review", "discount", "mrp", "detail",
                 "about", "fit", "this", "it", "off", "available", "stock", "material", "fabric", "worth"}


# ------------------------------------------------------------------ knowledge base
def _contact_line():
    return f"Phone: {OWNER['phone']}\nEmail: {OWNER['email']}"


def kb():
    """Each entry: id, kw (single words match tokens, phrases match text), answer, links."""
    sizes = {c: cat_sizes(c) for c in CAT_LABEL}
    return [
        dict(id="greet", kw=["hi", "hello", "hey", "hii", "hola", "namaste", "good morning", "good evening", "good afternoon", "sup"],
             a="Hi! I'm the Fashora assistant. I can help with products, sizes, delivery, returns, your cart and your account. What would you like to know?", links=[]),
        dict(id="thanks", kw=["thanks", "thank", "thx", "great", "awesome", "perfect", "nice", "cool", "ok thanks"],
             a="You're welcome! Anything else I can help you with?", links=[]),
        dict(id="bye", kw=["bye", "goodbye", "see you", "later", "good night"],
             a="Bye! Happy shopping at Fashora.", links=[]),
        dict(id="about", kw=["what is fashora", "about fashora", "about website", "about this website", "about the website", "about site", "this site",
                             "this website", "who are you", "what do you do", "what can you do", "how does the website work",
                             "how does this website work", "how does your website work", "how does the site work", "website work", "how it works", "how this works", "brand", "about us"],
             a=("Fashora is an online fashion store for men, women, kids and accessories. You can browse collections, open a product to pick colour, size and quantity, "
                "save favourites to your wishlist, add items to your cart and check out. I'm an automated assistant that answers common questions about the website."),
             links=[link("collections"), link("about")]),
        dict(id="order", kw=["how to order", "how do i order", "place order", "place an order", "how to buy", "how do i buy", "order process",
                             "how to purchase", "steps to order", "buy something", "make an order", "want to order", "order"],
             a=("Ordering is easy:\n1. Browse Shop or Collections and open a product.\n2. Choose colour, size and quantity.\n3. Tap Add to Cart.\n"
                "4. Open your Cart and review the items.\n5. Tap Proceed to Checkout to place the order."),
             links=[link("shop"), link("cart")]),
        dict(id="cart", kw=["cart", "add to cart", "remove", "delete item", "quantity", "qty", "clear cart", "change quantity", "basket", "bag"],
             a=("Your cart shows every item with its price. Use the + and - buttons to change quantity, the bin icon to remove an item, "
                "or Clear All to empty it. The cart icon at the top shows how many items you have."),
             links=[link("cart")]),
        dict(id="checkout", kw=["checkout", "check out", "pay", "payment", "payments", "cod", "cash on delivery", "upi", "card", "net banking", "how to pay", "payment options"],
             a=("Tap Proceed to Checkout at the bottom of your cart to place your order. "
                "For payment options (such as cash on delivery or UPI) and order confirmation, please contact the store team:\n" + _contact_line()),
             links=[link("cart"), link("contact")]),
        dict(id="shipping", kw=["shipping", "delivery", "deliver", "free delivery", "free shipping", "delivery charge", "delivery charges", "shipping charge",
                                "how long", "when will", "delivery time", "arrive", "dispatch", "courier"],
             a=(f"Delivery is free on orders above {money(FREE_SHIPPING)}. Any shipping charge appears in your Order Summary before you check out. "
                "Exact delivery time depends on your location, so please contact us with your pin code for an estimate."),
             links=[link("cart"), link("contact")]),
        dict(id="returns", kw=["return", "returns", "refund", "refunds", "exchange", "replace", "replacement", "7 day", "7 days", "money back", "wrong size", "damaged"],
             a=("We offer 7-day easy returns. If something doesn't fit or isn't right, contact us within 7 days of delivery with your order details "
                "and we'll guide you through the return, exchange or refund.\n" + _contact_line()),
             links=[link("contact")]),
        dict(id="size", kw=["size", "sizes", "size guide", "size chart", "which size", "find my size", "measurement", "measurements", "fit", "fitting"],
             a=("Sizes by category:\n" + "\n".join(f"- {CAT_LABEL[c]}: {', '.join('Free size' if x == 'Free' else x for x in s)}" for c, s in sizes.items()) +
                "\nEach product page shows the sizes available for that item. If you're between sizes, size up for a relaxed fit. "
                "For help choosing, contact us and we'll advise."),
             links=[link("shop"), link("contact")]),
        dict(id="account", kw=["login", "log in", "sign in", "signin", "register", "signup", "sign up", "account", "create account", "my account", "join"],
             a=("To create an account, open the person icon at the top, choose Create account and enter your name, email, optional mobile number and a password (6+ characters). "
                "Already registered? Choose Login and enter your email and password. Tip: on a phone, your browser can autofill these details."),
             links=[link("register"), link("login")]),
        dict(id="forgot", kw=["forgot", "forgot password", "reset password", "reset", "lost password", "change password", "cant login", "can't login", "unable to login"],
             a=("Online password reset isn't available yet. Please contact us from the email you registered with and we'll help you get back in:\n" + _contact_line()),
             links=[link("contact")]),
        dict(id="wishlist", kw=["wishlist", "wish list", "favorite", "favourite", "favorites", "favourites", "heart", "save for later", "saved items"],
             a=("Tap the heart on any product to save it to your wishlist, and tap it again to remove it. Open the heart icon at the top to see everything you saved. "
                "Your wishlist is kept in this browser while you shop."),
             links=[link("wishlist")]),
        dict(id="search", kw=["search", "find", "look for", "looking for", "filter", "sort", "browse", "where can i find"],
             a=("Use the search box on the Shop page to find a style by name, or tap a category chip (Men, Women, Kids, Accessories) to filter. "
                "You can also open Collections to browse by category."),
             links=[link("shop"), link("collections")]),
        dict(id="offers", kw=["offer", "offers", "discount", "discounts", "sale", "coupon", "coupons", "promo", "promo code", "deal", "deals", "cheap", "savings", "mrp", "off"],
             a=(f"Every product shows its MRP, our price and the % off. Delivery is free above {money(FREE_SHIPPING)}. "
                "I don't have any coupon codes listed right now - subscribe with your email in the footer to hear about new offers."),
             links=[link("shop")]),
        dict(id="contact", kw=["contact", "support", "help", "phone", "call", "email", "talk", "human", "agent", "customer care", "customer service",
                               "complaint", "complain", "reach", "whatsapp", "number", "address", "speak"],
             a=("Happy to connect you with the store team:\n" + _contact_line() + "\nOr send a message from the Contact page and we'll reply soon."),
             links=[link("contact")]),
        dict(id="track", kw=["track", "tracking", "where is my order", "order status", "status", "cancel", "cancel order", "my orders", "order history", "invoice", "bill"],
             a=("Online order tracking and order history aren't available yet. For an update on your order, or to cancel one, please contact us with the email you ordered with:\n" + _contact_line()),
             links=[link("contact")]),
        dict(id="blog", kw=["blog", "style tips", "tips", "trend", "trends", "article", "articles", "outfit ideas", "style guide", "read"],
             a=("Our blog has fashion tips and trend guides. Every article also lists matching products so you can shop the look straight from the post."),
             links=[link("blog")]),
        dict(id="newsletter", kw=["newsletter", "subscribe", "subscription", "updates"],
             a="Enter your email in the Newsletter box in the footer and tap the arrow to get updates and offers.", links=[]),
        dict(id="safe", kw=["secure", "safe", "safety", "privacy", "data", "trust", "trusted", "genuine", "legit", "fraud", "scam"],
             a=("Your password is stored in encrypted (hashed) form and checkout is secure. We only use the details you give us to run your account and orders."),
             links=[link("about")]),
        dict(id="quality", kw=["quality", "material", "fabric", "cotton", "durable", "premium"],
             a=("We focus on premium quality pieces made for all-day comfort. Fabric details are in each product's description - and if you need more, ask us on the Contact page."),
             links=[link("shop"), link("contact")]),
        dict(id="tech", kw=["not working", "error", "bug", "slow", "broken", "mobile", "phone app", "app", "tablet", "ios", "android", "laptop", "loading", "problem", "issue"],
             a=("Fashora works in any modern browser on phones, tablets and laptops. If something looks wrong, try refreshing the page or reopening it. "
                "If the problem continues, tell us what happened:\n" + _contact_line()),
             links=[link("contact")]),
        dict(id="owner", kw=["who made", "who built", "who created", "developer", "owner", "creator", "made by", "founder", "who owns"],
             a=f"Fashora was made by {OWNER['name']}.\n" + _contact_line(), links=[link("contact")]),
        dict(id="categories", kw=["categories", "category", "what do you sell", "what you sell", "collections", "collection", "catalog", "catalogue", "products",
                                  "what products", "what do you have", "items", "range", "what's new", "whats new", "new arrivals", "new"],
             a=("We sell:\n" + "\n".join(f"- {CAT_LABEL[c]} ({sum(1 for p in data.PRODUCTS if p['cat'] == c)} item{'s' if sum(1 for p in data.PRODUCTS if p['cat'] == c) != 1 else ''})" for c in CAT_LABEL) +
                "\nTap a category below to explore."),
             links=[link("cat", cat=c, name=CAT_LABEL[c]) for c in CAT_LABEL]),
    ]


KB = kb()
KB_BY_ID = {e["id"]: e for e in KB}


# ------------------------------------------------------------------ suggested questions
GENERIC_POOL = [
    "How do I place an order?", "Do you offer free delivery?", "What is your return policy?", "How do I find my size?",
    "How can I create an account?", "How does the wishlist work?", "What categories do you sell?", "Are there any offers right now?",
    "How can I contact support?", "How do I change quantity in my cart?", "Show me products under \u20b91500",
    "What are your top-rated products?", "Where can I read style tips?", "How do I search for a style?", "Is my data safe?",
]
PAGE_POOL = {
    "home": ["What categories do you sell?", "Do you offer free delivery?", "What are your top-rated products?", "Show me products under \u20b91500", "What is Fashora?"],
    "shop": ["How do I search for a style?", "Show me products under \u20b91500", "How do I find my size?", "How does the wishlist work?", "What are your top-rated products?"],
    "product": ["What sizes are available for this item?", "What is the price and discount of this?", "What colours does this come in?",
                "How do I add this to my cart?", "What is your return policy?", "Do you offer free delivery?"],
    "cart": ["How do I change quantity in my cart?", "How do I checkout?", "Is shipping free?", "What payment options are there?", "What is your return policy?"],
    "login": ["How can I create an account?", "I forgot my password", "Is my data safe?", "How do I login?"],
    "contact": ["How can I contact support?", "How do I track my order?", "What is your return policy?", "How do I cancel an order?"],
    "blog": ["Where can I read style tips?", "How do I shop the look from a blog post?", "What categories do you sell?"],
    "blog_post": ["How do I shop the look from a blog post?", "Where can I read style tips?", "What are your top-rated products?"],
    "wishlist": ["How does the wishlist work?", "How do I place an order?", "Show me products under \u20b91500"],
    "about": ["What is Fashora?", "Who made this website?", "How can I contact support?", "What is your return policy?"],
    "collections": ["What categories do you sell?", "How do I find my size?", "Show me products under \u20b91500"],
}


def suggestions(ep="", n=4, exclude=""):
    page_first = [q for q in PAGE_POOL.get(ep, []) if q != exclude]
    rest = [q for q in GENERIC_POOL if q not in page_first and q != exclude]
    random.shuffle(page_first)
    random.shuffle(rest)
    picked = page_first[: max(2, n - 2)]
    picked += rest[: n - len(picked)]
    random.shuffle(picked)
    return picked[:n]


def greeting(ep="", pid=None):
    p = PRODUCTS.get(pid) if pid else None
    if ep == "product" and p:
        text = f"Hi! I'm the Fashora assistant. Looking at the {p['name']}? Ask me about its size, colours, price or delivery."
    elif ep == "cart":
        text = "Hi! I'm the Fashora assistant. Need help with your cart, checkout or delivery?"
    elif ep == "login":
        text = "Hi! I'm the Fashora assistant. I can help you create an account or login."
    else:
        text = "Hi! I'm the Fashora assistant. Ask me anything about our products, sizes, delivery, returns or how the website works. Tap a question below or type your own."
    return text


# ------------------------------------------------------------------ answering
def _find_products(toks):
    ids = []
    for w in toks:
        for pid in PRODUCT_WORDS.get(w, ()):
            if pid not in ids:
                ids.append(pid)
    return [PRODUCTS[i] for i in ids]


def _budget(text):
    m = re.search(r"(?:under|below|within|less than|upto|up to|budget|max|cheaper than)\s*(?:rs\.?|inr|\u20b9)?\s*(\d[\d,]*)", text)
    if not m:
        m = re.search(r"(?:rs\.?|inr|\u20b9)\s*(\d[\d,]*)", text)
        if not m:
            return None
    try:
        return int(m.group(1).replace(",", ""))
    except ValueError:
        return None


POLICY_IDS = {"returns", "shipping", "checkout", "track", "cart", "wishlist", "forgot"}


def _kb_best(text, toks, only=None):
    """Best FAQ entry for this message -> (entry, score), or (None, 0) when nothing scores at least 2."""
    best, best_score = None, 0
    for e in KB:
        if only and e["id"] not in only:
            continue
        sc = 0
        for k in e["kw"]:
            if " " in k:
                if f" {k} " in text:
                    sc += 3
            elif k in toks:
                sc += 2
        if sc > best_score:
            best, best_score = e, sc
    return (best, best_score) if best_score >= 2 else (None, 0)


def _result(answer, links=None, ep="", asked=""):
    return {"answer": answer, "links": [resolve(l) for l in (links or [])], "suggestions": suggestions(ep, 3, asked)}


def answer(message, ep="", pid=None):
    message = (message or "").strip()[:300]
    text = norm(message)
    toks = tokens(text)
    pid = int(pid) if str(pid or "").isdigit() else None

    # 1) budget / recommendation questions
    budget = _budget(text)
    if budget:
        items = sorted((p for p in data.PRODUCTS if p["price"] <= budget), key=lambda p: p["price"])
        if items:
            return _result(f"Here are styles up to {money(budget)}:\n" + "\n".join("- " + product_line(p) for p in items[:5]),
                           [link("product", pid=p["id"], name=p["name"]) for p in items[:3]], ep, message)
        cheapest = min(data.PRODUCTS, key=lambda p: p["price"])
        return _result(f"Nothing is listed under {money(budget)} right now. Our most affordable style is {product_line(cheapest)}.",
                       [link("product", pid=cheapest["id"], name=cheapest["name"])], ep, message)
    if toks & {"best", "popular", "recommend", "recommendation", "suggest", "top", "bestseller", "trending", "gift", "favourite", "favorite"} \
            and toks & {"product", "products", "style", "styles", "rated", "seller", "sellers", "pick", "picks", "item", "items", "buy", "gift", "wear", "rating", "sold"} \
            or " top rated " in text or " top-rated " in text or " best seller" in text:
        top = sorted(data.PRODUCTS, key=lambda p: (-p["rating"], p["price"]))[:3]
        return _result("Our top-rated styles right now:\n" + "\n".join("- " + product_line(p) for p in top),
                       [link("product", pid=p["id"], name=p["name"]) for p in top], ep, message)

    # 2) a specific product is mentioned (unless the question is really about a policy / cart action)
    found = _find_products(toks)
    if found and _kb_best(text, toks, only=POLICY_IDS)[0] is None:
        found = found[:3]
        if len(found) == 1:
            p = found[0]
            return _result(product_detail(p), [link("product", pid=p["id"], name="View " + p["name"]), link("cart")], ep, message)
        return _result("Here's what we have:\n" + "\n".join("- " + product_line(p) for p in found),
                       [link("product", pid=p["id"], name=p["name"]) for p in found], ep, message)

    # 3) "this item" questions on a product page
    cur = PRODUCTS.get(pid) if ep == "product" and pid else None
    if cur and toks & CONTEXT_WORDS and not toks & {"return", "returns", "refund", "delivery", "shipping", "cart", "checkout", "pay", "payment", "wishlist", "account"}:
        if toks & {"size", "sizes", "fit"}:
            return _result(f"The {cur['name']} comes in: {', '.join(cur['sizes'])}.\nPick your size on the product page before adding it to your cart.", [link("product", pid=cur["id"], name="View this item")], ep, message)
        if toks & {"color", "colour", "colors", "colours"}:
            return _result(f"The {cur['name']} comes in {len(cur['colors'])} colour option{'s' if len(cur['colors']) != 1 else ''}. Tap the colour dots under the photo and the picture changes to match.", [], ep, message)
        return _result(product_detail(cur), [link("cart")], ep, message)

    # 4) category mentioned (men / women / kids / accessories)
    cats = [CAT_WORDS[w] for w in toks if w in CAT_WORDS]
    if cats and not toks & {"size", "sizes", "return", "returns", "delivery", "shipping"}:
        c = cats[0]
        items = [p for p in data.PRODUCTS if p["cat"] == c]
        return _result(f"{CAT_LABEL.get(c, c.title())}:\n" + "\n".join("- " + product_line(p) for p in items),
                       [link("cat", cat=c, name="See all " + CAT_LABEL.get(c, c.title()))], ep, message)

    # 5) FAQ knowledge base - best keyword score wins
    best, best_score = _kb_best(text, toks)
    if best:
        return _result(best["a"], best["links"], ep, message)

    # 6) fallback
    return _result("I'm not sure about that one yet. I can help with products, sizes, delivery, returns, your cart and your account - "
                   "or you can reach the store team directly:\n" + _contact_line(), [link("contact")], ep, message)


# ------------------------------------------------------------------ self-test:  python chatbot.py
if __name__ == "__main__":
    from flask import Flask

    t = Flask(__name__)
    t.add_url_rule("/", "home", lambda: "")
    for name, rule in [("shop", "/shop"), ("cart", "/cart"), ("contact", "/contact"), ("login", "/login"), ("wishlist", "/wishlist"),
                       ("blog", "/blog"), ("about", "/about"), ("collections", "/collections"), ("product", "/product/<int:pid>")]:
        t.add_url_rule(rule, name, lambda **k: "")
    bad = 0
    with t.test_request_context():
        for ep, qs in list(PAGE_POOL.items()) + [("generic", GENERIC_POOL)]:
            for q in qs:
                r = answer(q, ep if ep != "generic" else "", 1 if ep == "product" else None)
                if r["answer"].startswith("I'm not sure"):
                    bad += 1
                    print("UNANSWERED:", ep, "->", q)
    print("all suggested questions answered" if not bad else f"{bad} unanswered")
