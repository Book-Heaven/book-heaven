#!/usr/bin/env python3
"""Rebuilds every Book Heaven page, the sitemap and robots.txt.

Edit tools/books.json or tools/pages/*.html, then run:  python3 tools/build.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://book-heaven.pages.dev/"
TODAY = "2026-11-28"          # sitemap <lastmod>; update when content changes
SPOTLIGHTS = {"phil-matarese": {"published": "2026-11-27", "book": "growing-up-pentecostal-a-memoir"}}
COLS = ["#3b5d3a", "#8a2f2f", "#2f4a6b", "#b5762e", "#4a3a5e", "#2e5e5a", "#7a3b52"]
HOME_COUNT = 13               # books shown on the homepage shelf

def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, text):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)

BOOKS = json.loads(read("tools/books.json"))
FAQ = json.loads(read("tools/faq.json"))
e = lambda t: html.escape(t, quote=True)
plain = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t))
absolute = lambda u: u if u.startswith("http") else SITE + u
local = lambda u, r: u if u.startswith("http") else r + u

def clip(text, n=155):
    text = " ".join(text.split())
    if len(text) <= n: return text
    return text[:n - 1].rsplit(" ", 1)[0].rstrip(",;:—-.") + "…"

AUTHORS = {}
for b in BOOKS: AUTHORS.setdefault(b["authorSlug"], []).append(b)

def has_bio(books):
    bio = books[0]["bio"]
    return bool(bio) and "coming soon" not in bio and "does not provide" not in bio

def dims(b): return f' width="{b["w"]}" height="{b["h"]}"' if b.get("w") else ""

ORG = {"@type": "Organization", "@id": SITE + "#organization", "name": "Book Heaven", "url": SITE,
       "logo": SITE + "assets/img/logo.jpg",
       "description": "An independent book-discovery and author-feature publication."}
WEB = {"@type": "WebSite", "@id": SITE + "#website", "name": "Book Heaven", "url": SITE,
       "publisher": {"@id": SITE + "#organization"}, "inLanguage": "en"}

def people(b):
    out = []
    for name in b["author"].split(" & "):
        m = re.match(r"(.+?) \((.+)\)$", name)
        p = {"@type": "Person", "name": m.group(1) if m else name, "url": SITE + f"authors/{b['authorSlug']}/"}
        if m: p["alternateName"] = m.group(2)
        out.append(p)
    return out

def book_ld(b):
    d = {"@type": "Book", "@id": SITE + f"books/{b['slug']}/#book", "name": b["title"], "url": SITE + f"books/{b['slug']}/",
         "author": people(b), "genre": b["genre"], "image": absolute(b["cover"])}
    if b["about"]: d["description"] = b["about"]
    if b["publisher"]: d["publisher"] = {"@type": "Organization", "name": b["publisher"]}
    return d

NAV = [("", "Home"), ("books/", "Books"), ("authors/", "Authors"), ("interviews/", "Conversations"), ("about/", "About"), ("contact/", "Contact")]

def page(path, title, desc, body, r, *, ld=(), crumbs=(), image=None, og_type="website", index=True, current=None, home=False):
    url = SITE + path
    img = absolute(image) if image else SITE + "assets/img/og-book-heaven.jpg"
    graph = [ORG, WEB]
    if crumbs:
        trail = [("Home", "")] + list(crumbs)
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(trail)]})
        parts = [f'<a href="{r + p or "./"}">{e(n)}</a>' for n, p in trail[:-1]] + [f'<span aria-current="page">{e(trail[-1][0])}</span>']
        bar = f'<nav class="crumbs wrap" aria-label="Breadcrumb" style="display:block;height:auto">{" / ".join(parts)}</nav>\n'
    else:
        bar = ""
    graph += list(ld)
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", "\\u003c")
    home_href = r or "./"
    if path == "404.html": home_href = "/"
    cur = lambda p: ' aria-current="page"' if p == current else ""
    menu = "".join(f'<li><a href="{r + p if p else home_href}"{cur(p)}>{n}</a></li>' for p, n in NAV)
    logo = f'<img class="lm" src="{r}assets/img/logo.jpg" width="420" height="188" alt="">'
    redirect = ""
    if home:
        old = {"p-books": "books/", "p-authors": "authors/", "p-conversations": "interviews/", "p-about": "about/",
               "p-contact": "contact/", "p-phil-matarese": "authors/phil-matarese/"}
        # Positions match the old #p-book-N links that have already been shared.
        for i, s in enumerate(LEGACY): old[f"p-book-{i}"] = f"books/{s}/"
        redirect = ("<script>(function(){var m=" + json.dumps(old, separators=(",", ":")) +
                    ';function go(){var t=m[location.hash.slice(1)];if(t)location.replace(t)}go();addEventListener("hashchange",go)})();</script>\n')
    meta = [f'<meta name="description" content="{e(desc)}">']
    if index:
        meta.append(f'<link rel="canonical" href="{url}">')
    else:
        meta.append('<meta name="robots" content="noindex,follow">')
    card = "summary" if image else "summary_large_image"
    meta += [f'<meta property="og:site_name" content="Book Heaven">', f'<meta property="og:type" content="{og_type}">',
             f'<meta property="og:title" content="{e(title)}">', f'<meta property="og:description" content="{e(desc)}">',
             f'<meta property="og:image" content="{e(img)}">',
             f'<meta name="twitter:card" content="{card}">', f'<meta name="twitter:title" content="{e(title)}">',
             f'<meta name="twitter:description" content="{e(desc)}">', f'<meta name="twitter:image" content="{e(img)}">']
    if index: meta.append(f'<meta property="og:url" content="{url}">')
    meta = "\n".join(meta)
    main = f'<main id="v-home">\n{body}\n</main>' if home else f'<main id="pv">\n{bar}{body}\n</main>'
    extra = f'<script src="{r}assets/js/home.js" defer></script>\n' if home else ""
    write(path + "index.html" if path == "" or path.endswith("/") else path, f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{redirect}<title>{e(title)}</title>
{meta}
<link rel="icon" type="image/svg+xml" href="{r}favicon.svg?v=20261123">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/site.css">
<script>try{{var t=localStorage.getItem("bh-theme");if(t)document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<script type="application/ld+json">{data}</script>
</head>
<body>
<div class="ann">Fresh picks every week &middot; Find your next favourite read today</div>
<div id="pg"></div>
<div class="navbar"><div class="wrap">
 <a class="skip" href="#{"v-home" if home else "pv"}">Skip to content</a>
 <nav aria-label="Main">
  <a class="logo" href="{home_href}" aria-label="Book Heaven home">{logo}<span>Book <b>Heaven</b></span></a>
  <ul>{menu}</ul>
  <span style="display:flex;gap:10px;align-items:center"><a class="btn" href="{r}contact/">Submit</a><button id="bu" class="ic burger" aria-label="Open menu" aria-expanded="false">&#9776;</button><button id="th" class="ic" aria-label="Switch between light and dark theme">&#9680;</button></span>
 </nav>
</div></div>
{main}
<footer><div class="wrap">
 <div class="fg">
  <div><div class="logo">{logo.replace('alt=""', 'loading="lazy" alt=""')}<span>Book <b>Heaven</b></span></div><p style="opacity:.75;margin-top:6px">Every Book Has a Story Beyond Its Pages.</p></div>
  <form class="sub" data-news novalidate>
   <input type="email" placeholder="Your email" aria-label="Email" required><button class="btn">Subscribe</button>
  </form>
 </div>
 <div class="fl"><a href="{r}books/">Books</a><a href="{r}authors/">Authors</a><a href="{r}interviews/">Conversations</a><a href="{r}author-interviews/">Interview opportunities</a><a href="{r}editorial/">Editorial</a><a href="{r}faq/">FAQ</a><a href="{r}about/">About</a><a href="{r}contact/">Contact</a><span>Every book has another story behind it.</span></div>
</div></footer>
<script src="{r}assets/js/site.js" defer></script>
{extra}<script src="{r}assets/js/snow.js" defer></script>
</body>
</html>
''')

def tile(b, i, r, lazy=True):
    return (f'<a class="bk" href="{r}books/{b["slug"]}/" data-genre="{e(b["genre"].lower())}" data-search="{e((b["title"] + " " + b["author"]).lower())}">'
            f'<div class="cover" style="background:{COLS[i % 7]};padding:0;overflow:hidden"><img src="{e(local(b["cover"], r))}" alt="{e(b["title"])} by {e(b["author"])}, book cover"{dims(b)}'
            f'{" loading=\"lazy\"" if lazy else ""} style="width:100%;height:100%;object-fit:cover"></div><small>{e(b["title"])}<br>{e(b["author"])}<br>{e(b["genre"])}</small></a>')

def head(eyebrow, h1, lead):
    return f'<div class="ptitle"><p class="eyebrow" style="color:var(--red)">{eyebrow}</p><h1 class="serif">{h1}</h1><p class="lead">{lead}</p></div>'

def section(label, title, inner): return f'<div class="sc2"><p class="eyebrow">{label}</p><h2>{title}</h2>{inner}</div>'
def fragment(name, r): return read(f"tools/pages/{name}.html").replace("{r}", r)

LEGACY = ["the-lost-ones", "icy-control", "the-witch", "state-of-terror", "1-percent-lifesteal-5", "the-long-witch-goodnight",
          "murder-mystery-advent-calendar-the-killer-checked-in", "darkness-of-dragons-a-graphic-novel", "the-naughty-list-agreement",
          "the-collateral-heart", "strangers-on-the-mountain", "the-wrong-daughter", "growing-up-pentecostal-a-memoir",
          "he-who-fights-with-monsters-book-eight", "the-good-daughter", "journey-to-joy-march-september-1872", "beyond-what-is-given"]

def build():
    indexed = []
    def add(path, *a, **k):
        page(path, *a, **k)
        if k.get("index", True): indexed.append(path)

    by = {b["slug"]: b for b in BOOKS}
    # ---------- home
    shelf = BOOKS[:HOME_COUNT]
    bks = "".join(tile(b, i, "") for i, b in enumerate(shelf))
    phil = by["growing-up-pentecostal-a-memoir"]
    def art_img(b): return f'<div class="sp"><img src="{e(b["cover"])}" alt="{e(b["title"])} book cover"{dims(b)} loading="lazy"></div>'
    arts = (f'<article class="art"><a href="authors/phil-matarese/">{art_img(phil)}</a><p class="eyebrow">SPOTLIGHT &middot; MEMOIR</p><h3><a href="authors/phil-matarese/">Phil Matarese</a></h3>'
            '<p>An honest journey through childhood faith, spiritual discovery, and the courage to examine what we believe.</p><p class="meta"><a class="link" href="authors/phil-matarese/">Read the full feature &rarr;</a></p>'
            f'<p class="meta"><a class="link" href="books/{phil["slug"]}/">View the book &rarr;</a></p></article>')
    for b in shelf[:6]:
        arts += (f'<article class="art">{art_img(b)}<p class="eyebrow">SPOTLIGHT &middot; {e(b["genre"].upper())}</p><h3><a href="books/{b["slug"]}/">{e(b["title"])}</a></h3>'
                 f'<p>By {e(b["author"])}. A {e(b["genre"].lower())} pick from our shelf.</p><p class="meta"><a class="link" href="{b["buy"]}" target="_blank" rel="noopener sponsored">Discover the Book &rarr;</a></p></article>')
    rows = ""
    for n, k in enumerate((0, 2, 3)):
        b = BOOKS[k]; a = f'href="{b["buy"]}" target="_blank" rel="noopener sponsored"'
        rows += (f'<div class="row"><span class="n">0{n+1}</span><a {a}><img src="{e(b["cover"])}" alt="{e(b["title"])} cover"{dims(b)} loading="lazy"></a><div><h3 class="serif"><a {a}>{e(b["title"])}</a></h3>'
                 f'<p>{e(b["author"])} &middot; {e(b["genre"])}</p></div><a class="btn" {a}>View on Amazon</a></div>')
    home = read("tools/pages/home.html").replace("{r}", "").replace('href=""', 'href="./"')
    home = home.replace("{count}", str(len(shelf))).replace("{bks}", bks).replace("{arts}", arts).replace("{rows}", rows)
    add("", "Book Heaven | Book Recommendations, Features & Author Stories",
        "Discover book recommendations, book features and author spotlights. Authors can submit a book or ask about a written email interview with Book Heaven.",
        home, "", current="", home=True)

    # ---------- books
    r = "../"
    cats = [("", "All"), ("roman", "Romance"), ("myst|thrill", "Mystery &amp; thriller"), ("fant", "Fantasy"), ("histor", "Historical")]
    pills = "".join(f'<a href="#pbk" data-pg="{k}"{" class=\"on\"" if not k else ""}>{n}</a>' for k, n in cats)
    body = ('<div class="wrap">' + head("LIBRARY", "Books", "Every book on the shelf. Pick a category, then open a book for its page.") +
            f'<div class="pills" id="pcat" style="margin-top:20px">{pills}</div><h2 class="sr">All featured books</h2><div class="books" id="pbk" style="margin-top:28px;padding-bottom:72px">' +
            "".join(tile(b, i, r, i > 5) for i, b in enumerate(BOOKS)) + "</div></div>")
    add("books/", "Book Recommendations & Featured Books | Book Heaven",
        "Browse Book Heaven’s featured books, including romance, mystery, thriller, fantasy, historical fiction and memoir, with a page for every title.",
        body, r, crumbs=[("Books", "books/")], current="books/",
        ld=[{"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + f"books/{b['slug']}/", "name": b["title"]} for i, b in enumerate(BOOKS)]}])

    r = "../../"
    for b in BOOKS:
        none = f'<p>The full details for this book are on its {b["retailer"]} page. Use the retailer button above.</p>'
        para = lambda t: f"<p>{e(t)}</p>" if t else none
        label = "Get it at Barnes & Noble" if b["retailer"] == "Barnes & Noble" else "Get it on Amazon"
        profile = f'<p><a class="link" href="{r}authors/{b["authorSlug"]}/">More about {e(b["author"])} &rarr;</a></p>'
        last = (section("Author spotlight", "Meet the author", f'<p><a class="link" href="{r}authors/{b["authorSlug"]}/">Read the full author spotlight &rarr;</a></p>')
                if b["authorSlug"] in SPOTLIGHTS else section("Conversation", "Related interview", "<p>Coming soon.</p>"))
        body = (f'<div class="wrap"><a class="back" href="{r}books/">&larr; All books</a><div class="det"><aside><img class="big" src="{e(local(b["cover"], r))}" alt="{e(b["title"])} by {e(b["author"])}, book cover"{dims(b)} fetchpriority="high"></aside><div>'
                f'<span class="tag">{e(b["genre"])}</span><h1 class="serif" style="margin-top:12px">{e(b["title"])}</h1><p class="meta" style="font-size:15px">by <a href="{r}authors/{b["authorSlug"]}/">{e(b["author"])}</a></p>'
                + (f'<p class="meta">Publisher: {e(b["publisher"])}</p>' if b["publisher"] else "") +
                f'<div style="margin:18px 0 0"><a class="btn" href="{b["buy"]}" target="_blank" rel="noopener sponsored">{e(label)}</a></div>'
                + section("Genre", "Genre", f'<p>{e(b["genre"])}</p>') + section("The book", "About the book", para(b["about"]))
                + section("The author", "About the author", (f'<p>{e(b["bio"])}</p>' if b["bio"] else none) + profile)
                + section("Why it matters", "Why the book matters", para(b["why"])) + last + "</div></div></div>")
        desc = b["about"] or f'{b["title"]} by {b["author"]}: {b["genre"].lower()}. {b["why"]} See the book page and retailer link on Book Heaven.'
        short = b["title"] if len(b["title"]) <= 45 else b["title"].split(":")[0]
        add(f"books/{b['slug']}/", f"{short} by {b['author']} | Book Heaven", clip(desc), body, r,
            crumbs=[("Books", "books/"), (b["title"], f"books/{b['slug']}/")], current="books/", image=b["cover"], og_type="book", ld=[book_ld(b)])

    # ---------- authors
    r = "../"
    rows = ""
    for slug, bs in AUTHORS.items():
        titles = " &middot; ".join(f'<a class="link" href="{r}books/{b["slug"]}/">{e(b["title"])}</a>' for b in bs)
        note = (f'<p class="meta"><a class="link" href="{r}authors/{slug}/">Read the author spotlight &rarr;</a></p>' if slug in SPOTLIGHTS
                else '<p class="meta">Author feature coming soon</p>')
        rows += f'<div class="arow"><h2 class="serif"><a href="{r}authors/{slug}/">{e(bs[0]["author"])}</a></h2><p>{titles}</p>{note}</div>'
    body = ('<div class="wrap">' + head("DIRECTORY", "Authors", "The writers behind the books on our shelf. Full author features are coming soon.") +
            f'<div style="padding-bottom:72px">{rows}</div></div>')
    add("authors/", "Featured Authors & Their Books | Book Heaven",
        "Meet the writers behind the books on Book Heaven’s shelf, explore their featured titles and read our author spotlights.",
        body, r, crumbs=[("Authors", "authors/")], current="authors/")

    r = "../../"
    for slug, bs in AUTHORS.items():
        b = bs[0]; name = b["author"]; path = f"authors/{slug}/"
        crumbs = [("Authors", "authors/"), (name, path)]
        if slug in SPOTLIGHTS:
            info = SPOTLIGHTS[slug]; bk = by[info["book"]]
            headline = f"{name}: Exploring Faith, Reflection, and {bk['title'].split(':')[0]}"
            desc = "Author spotlight: Phil Matarese on Growing Up Pentecostal: A Memoir, writing with honesty and respect, and examining what we believe."
            person = {**people(b)[0], "@id": SITE + path + "#person", "description": b["bio"]}
            art = {"@type": "Article", "headline": headline, "description": desc, "image": absolute(bk["cover"]),
                   "datePublished": info["published"], "dateModified": TODAY, "mainEntityOfPage": SITE + path,
                   "author": {"@id": SITE + "#organization"}, "publisher": {"@id": SITE + "#organization"},
                   "about": [{"@id": SITE + path + "#person"}, {"@id": SITE + f"books/{bk['slug']}/#book"}]}
            add(path, "Phil Matarese Author Spotlight | Book Heaven", desc, fragment(slug, r), r, crumbs=crumbs, current="authors/",
                image=bk["cover"], og_type="article", ld=[person, art, book_ld(bk)])
            continue
        bio = f"<p>{e(b['bio'])}</p>" if b["bio"] else "<p>An author biography is coming soon.</p>"
        grid = "".join(tile(x, BOOKS.index(x), r, False) for x in bs)
        body = ('<div class="wrap">' + head("AUTHOR", e(name), f"Featured on Book Heaven for {e(', '.join(x['title'] for x in bs))}.") +
                f'<div class="prose" style="padding-bottom:0"><h2>About the author</h2>{bio}<h2>Featured on our shelf</h2></div>'
                f'<div class="books" style="margin-top:16px;padding-bottom:72px">{grid}</div></div>')
        ps = [{**p, "@id": SITE + path + f"#person-{i+1}"} for i, p in enumerate(people(b))]
        add(path, f"{name}: Author Profile | Book Heaven", clip(b["bio"] or f"{name}, author of {b['title']}, on Book Heaven."), body, r,
            crumbs=crumbs, current="authors/", index=has_bio(bs), ld=ps)

    # ---------- information pages
    r = "../"
    interviews = fragment("interviews", r).replace('<h2>What we ask authors about</h2>',
        f'<p>Read how to take part on our <a class="link" href="{r}author-interviews/">author interview opportunities</a> page.</p><h2>What we ask authors about</h2>')
    add("interviews/", "Author Interviews & Conversations | Book Heaven",
        "How Book Heaven author conversations work, what we ask writers about, and how we confirm every answer in the author’s own voice.",
        interviews, r, crumbs=[("Conversations", "interviews/")], current="interviews/")
    add("about/", "About Book Heaven: Our Purpose & Editorial Process",
        "Book Heaven is an independent book-discovery and author-feature publication run by its founder. Learn what we do and how we work.",
        fragment("about", r), r, crumbs=[("About", "about/")], current="about/",
        ld=[{"@type": "AboutPage", "name": "About Book Heaven", "url": SITE + "about/", "about": {"@id": SITE + "#organization"}}])
    add("contact/", "Submit Your Book & Contact Book Heaven",
        "Send Book Heaven your book details, suggest an author conversation or ask a question. Submitting for editorial consideration is free.",
        fragment("contact", r), r, crumbs=[("Contact", "contact/")], current="contact/")
    add("author-interviews/", "Author Interview Opportunities for Independent Authors | Book Heaven",
        "Independent and traditionally published authors can ask to be considered for a written email interview. No fee to be considered; selection is not guaranteed.",
        fragment("author-interviews", r), r, crumbs=[("Author interview opportunities", "author-interviews/")])
    qa = "".join(f'<details open><summary>{q}</summary><p>{a.replace(" above this FAQ section", " on our homepage")}</p></details>' for q, a in FAQ)
    add("faq/", "Frequently Asked Questions | Book Heaven",
        "Answers about the books Book Heaven features, author submissions and interviews, costs, where to buy books and the Reading Circle.",
        '<div class="wrap">' + head("A LITTLE CLARITY", "Frequently asked questions", "For readers and authors.") +
        f'<div class="faq" style="margin:24px 0 72px">{qa}</div></div>', r, crumbs=[("FAQ", "faq/")],
        ld=[{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a.replace(" above this FAQ section", " on our homepage"))}} for q, a in FAQ]}])
    phil_row = (f'<div class="arow"><p class="eyebrow">AUTHOR SPOTLIGHT &middot; MEMOIR</p><h2 class="serif"><a href="{r}authors/phil-matarese/">Phil Matarese: Exploring Faith, Reflection, and <em>Growing Up Pentecostal</em></a></h2>'
                f'<p>An honest journey through childhood faith, spiritual discovery, and the courage to examine what we believe.</p><p class="meta"><a class="link" href="{r}authors/phil-matarese/">Read the full feature &rarr;</a></p></div>')
    add("editorial/", "Editorial: Author Spotlights & Book Features | Book Heaven",
        "Read Book Heaven’s editorial features and author spotlights about books, writing journeys and the stories behind them.",
        '<div class="wrap">' + head("EDITORIAL", "Author spotlights and book features", "Stories about books and the people who write them.") +
        f'<div style="padding-bottom:72px">{phil_row}</div></div>', r, crumbs=[("Editorial", "editorial/")])

    page("404.html", "Page not found | Book Heaven", "This Book Heaven page could not be found.",
         '<div class="wrap" style="padding-bottom:72px">' + head("404", "Page not found", "The page may have moved. Browse the books or return home.") +
         '<p style="margin-top:20px"><a class="btn" href="/books/">Browse books</a> <a class="link" href="/" style="margin-left:14px">Home</a></p></div>',
         "/", index=False)

    urls = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in indexed)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}sitemap.xml\n")
    write("_headers", "/assets/*\n  Cache-Control: public, max-age=86400\n\n/tools/*\n  X-Robots-Tag: noindex\n")
    print(len(indexed), "indexable pages built")

if __name__ == "__main__": build()
