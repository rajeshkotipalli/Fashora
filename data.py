"""EDIT ME: site content. Image names are relative to static/images/ - drop your files there."""
def imgs(n, k=4): return [f"products/{n}-{i+1}.jpg" for i in range(k)]

HERO = ["hero/hero-1.jpg", "hero/hero-2.jpg", "hero/hero-3.jpg"]  # slides whose file is missing are skipped automatically
COLLECTIONS = [
    {"name": "Men's Fashion", "cat": "men", "img": "products/hoodie-1.jpg"},
    {"name": "Women's Fashion", "cat": "women", "img": "products/dress-2.jpg"},
    {"name": "Kids Wear", "cat": "kids", "img": "products/kids-3.jpg"},
    {"name": "Accessories", "cat": "accessories", "img": "products/acc-1.jpg"},
]
ARRIVALS = ["products/jacket-1.jpg", "products/dress-1.jpg", "products/knit-1.jpg", "products/hoodie-1.jpg"]
ABOUT_IMG, LOGIN_IMG = "about/store.jpg", "login/login.jpg"
PRODUCTS = [
    dict(id=1, name="Premium Oversized Hoodie", cat="men", sub="Hoodie", price=1499, mrp=2499, rating=4.8, reviews="12k",
         desc="Stay cozy and stylish with our premium oversized hoodie. Made with high-quality fabric for all-day comfort.",
         colors=["#5b2b4d", "#f3f3f3", "#161616"], cimg=[0, 1, 2], sizes=["S", "M", "L", "XL", "XXL"], images=imgs("hoodie")),
    dict(id=2, name="Classic White T-Shirt", cat="men", sub="T-Shirt", price=799, mrp=1199, rating=4.6, reviews="8k",
         desc="A soft, breathable everyday tee that goes with everything.", colors=["#ffffff", "#2f5fc4"], cimg=[0, 2], sizes=["S", "M", "L", "XL"], images=imgs("tshirt")),
    dict(id=3, name="Denim Jacket", cat="men", sub="Jacket", price=2499, mrp=3299, rating=4.7, reviews="5k",
         desc="Structured denim jacket with a relaxed modern fit.", colors=["#8fb4d9", "#1a1a1a", "#b88c5a"], cimg=[0, 1, 2], sizes=["S", "M", "L", "XL"], images=imgs("jacket")),
    dict(id=4, name="Sweatshirt", cat="men", sub="Sweatshirt", price=1299, mrp=1799, rating=4.5, reviews="3k",
         desc="Warm fleece-lined sweatshirt in a neutral tone.", colors=["#e8dcc0", "#1b2a4a"], cimg=[0, 3], sizes=["S", "M", "L", "XL"], images=imgs("sweatshirt")),
    dict(id=5, name="Summer Red Dress", cat="women", sub="Dress", price=1899, mrp=2599, rating=4.8, reviews="6k",
         desc="Flowy red dress made for warm evenings.", colors=["#b8302a", "#1f2f5c", "#8fa88a"], cimg=[0, 2, 3], sizes=["XS", "S", "M", "L"], images=imgs("dress")),
    dict(id=6, name="Cream Knit Top", cat="women", sub="Top", price=1199, mrp=1599, rating=4.4, reviews="2k",
         desc="Soft knit top that layers with anything.", colors=["#efe6d6", "#cdb899"], cimg=[0, 3], sizes=["XS", "S", "M", "L"], images=imgs("knit")),
    dict(id=7, name="Kids Grey Hoodie", cat="kids", sub="Hoodie", price=999, mrp=1399, rating=4.6, reviews="4k",
         desc="Easy-wear hoodie for active kids.", colors=["#b8bbbf", "#2b2b2b"], cimg=[0, 1], sizes=["4Y", "6Y", "8Y", "10Y"], images=imgs("kids")),
    dict(id=8, name="Black Cap & Sunglasses Set", cat="accessories", sub="Set", price=1099, mrp=1499, rating=4.3, reviews="1k",
         desc="Cap and sunglasses set to finish any look.", colors=["#111111"], cimg=[0], sizes=["Free"], images=imgs("acc")),
]
# ---- site owner (shown in footer, contact page and About) - edit here once ----
OWNER = dict(name="K Rajesh", phone="93466674777", email="k94586034@gmail.com")

def post(slug, title, date, cat, img, excerpt, body, shop, read="4 min read", pos="center"):
    return dict(slug=slug, title=title, date=date, cat=cat, img=img, excerpt=excerpt, body=body, shop=shop, read=read, pos=pos)

# newest first. Lines starting with "## " become sub-headings.
BLOGS = [
    post("must-have-outfits", "5 Must-Have Outfits This Season", "Nov 20, 2024", "Outfits", "blog/1.jpg",
         "Five easy outfits that take you from college to dinner without a wardrobe change.",
         ["A good wardrobe is built from a few pieces that work hard. Start with an oversized hoodie, straight-fit denim and clean white sneakers, then repeat the formula in different colours.",
          "## 1. The weekend hoodie look", "Pair an oversized hoodie with relaxed trousers and a cap. It is comfortable, current and takes no effort.",
          "## 2. Denim on denim", "Layer a denim jacket over a plain white tee for an effortless day look, then swap the tee for a crisp polo in the evening.",
          "## 3. The flowy dress", "A wrap dress needs nothing more than sunglasses and flat sandals. Choose a print that works in daylight and at dinner.",
          "## 4. Cosy knit and beige", "A cable knit with straight beige trousers is the easiest smart-casual outfit there is.",
          "## 5. Keep colours simple", "Black, white, beige and one accent such as forest green or burgundy will make every piece match every other piece."],
         [1, 3, 5], pos="center"),
    post("style-oversized", "How to Style Oversized Clothes", "Nov 18, 2024", "Styling", "blog/2.jpg",
         "Oversized does not mean shapeless. Here is how to keep the proportions right.",
         ["Oversized clothes are comfortable, but they can swallow you if the proportions are wrong. These rules keep the look sharp.",
          "## Balance the volume", "If the top is oversized, keep the bottom slim or straight. A big sweater with pleated trousers is a good example.",
          "## Show a little skin", "Push up a sleeve or show an ankle so the outfit still has structure and you do not disappear into the fabric.",
          "## Define the waist", "Add a fitted layer, a belt or a bag strap across the body to create shape.",
          "## Finish with accessories", "Sunglasses, a cap or a watch pull an oversized outfit together and make it look planned."],
         [1, 4, 6], pos="center"),
    post("fashion-trends-2025", "Top 10 Fashion Trends in 2025", "Nov 15, 2024", "Trends", "blog/3.jpg",
         "From earthy greens to relaxed tailoring, these are the looks everyone is wearing next year.",
         ["Fashion is moving towards comfort, quality and colours that feel natural. Here is what to expect.",
          "## Earth tones lead", "Forest green, warm beige and chocolate brown are on every rack, and they mix easily with each other.",
          "## Relaxed tailoring", "Soft blazers, wide-leg jeans and oversized silhouettes keep replacing tight fits.",
          "## Knitwear everywhere", "Chunky cable knits and neutral cardigans work from office to weekend.",
          "## Simple accessories", "Clean caps, slim sunglasses, simple watches and structured bags beat loud logos."],
         [5, 6, 8], pos="center"),
    post("capsule-wardrobe", "Build a Capsule Wardrobe in 10 Pieces", "Nov 10, 2024", "Styling", "products/knit-1.jpg",
         "Fewer clothes, more outfits. A simple 10-piece formula that works all year.",
         ["A capsule wardrobe is a small set of clothes that all go together, so getting dressed takes a minute.",
          "## Pick your colours", "Choose a base colour, one neutral and one accent, then buy pieces that match at least three others.",
          "## The 10 pieces", "Two tees, one knit, one sweatshirt, one hoodie, one jacket, one pair of denim, one pair of trousers, one dress or shirt and one pair of clean sneakers.",
          "## Spend where it counts", "Invest in outerwear and shoes, and save money on basics like tees."],
         [6, 2, 3], read="3 min read", pos="center 25%"),
    post("winter-layering", "Winter Layering Without the Bulk", "Nov 5, 2024", "Outfits", "products/jacket-1.jpg",
         "Stay warm and sharp with thin layers that actually look good together.",
         ["The secret to winter style is thin layers rather than one thick coat.",
          "## Start light", "Begin with a soft base layer such as a plain tee or fine knit.",
          "## Add warmth", "Put a sweatshirt or knit on top, then finish with a structured jacket like a sherpa-lined denim jacket.",
          "## Mix textures", "Fleece, denim and knit together add depth, so the outfit looks rich even in neutral colours."],
         [3, 4, 1], read="3 min read", pos="center 20%"),
    post("accessories-guide", "5 Accessories That Finish Any Look", "Oct 28, 2024", "Accessories", "products/acc-1.jpg",
         "A cap, sunglasses and a watch can lift the simplest outfit. Here is how to choose them.",
         ["Accessories are the quickest way to make a basic outfit look styled.",
          "## A plain black cap", "It works with hoodies, tees and jackets, and it hides a bad hair day.",
          "## Sunglasses that fit your face", "Wayfarer shapes suit most faces. Keep frames dark and simple.",
          "## A clean watch", "Choose a black or silver dial with a leather or mesh strap, and it goes with everything.",
          "## Match the metals", "Keep buckles, watch case and frame details in one colour family so the set looks planned."],
         [8, 1], read="3 min read", pos="center 15%"),
]
