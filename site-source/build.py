"""Generate the IBuyRedding replacement website preview from the REI template default.

Inputs (snapshot of the public ibuyredding.com site, read 16 November 2026, kept outside this repo):
  home.html, about.html, faq.html, sell-inherited-house-redding.html, local-businesses-in-redding--ca.html,
  privacy-policy.html and posts.json (all 145 blog posts from the site's own page data),
plus site-source/funnel-original.html for the multi-situation assessment.

Every page keeps its original path, title, meta description, canonical and body copy.
Preview pages stay noindex until the approved production deployment.
"""
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from datetime import datetime
import json, re, html, os, csv

ROOT = Path(__file__).resolve().parents[1]
BASE = '/ibuyredding-funnel/'
ORIGIN = 'https://ibuyredding.com'
PREVIEW = 'https://andrewpcherry.github.io' + BASE
RAW = Path(os.environ.get('IBR_SNAPSHOT', ROOT.parent / 'ibuyredding-snapshot-2026-11-16'))
esc = html.escape
CSS_V = '20261116a'

BRAND = 'IBuyRedding'
OWNER = 'Manzo Capital LLC'
PERSON, PERSON_FULL = 'Oscar', 'Oscar Manzo'
PHONE, TEL = '(530) 638-2296', 'tel:+15306382296'
MARKET = 'Redding &amp; Northern California'
# Google Business Profile "IBuyRedding- Sell my home fast!", as embedded on ibuyredding.com (scraped by the site 17 April 2026): 5 stars, 12 reviews.
GOOGLE_URL = 'https://www.google.com/maps?cid=17598463580441016117'
G_RATING, G_COUNT = '5.0', '12'
COUNTIES = {
    'Shasta County': 'Redding, Anderson, Shasta Lake, Red Bluff, Cottonwood, Bella Vista, Palo Cedro, Shingletown, Mountain Gate, Lakehead, Burney, Millville, McArthur, Round Mountain, Whitmore, Fall River Mills, Montgomery Creek, Big Bend.',
    'Tehama County': 'Corning, Los Molinos, Tehama, Gerber, Lake California, Mineral, Manton, Mill Creek, Paskenta, Proberta, Rancho Tehama Reserve, Vina.',
    'Siskiyou County': 'Yreka, Mount Shasta, Weed, Dorris, Tulelake, Montague, Etna, Fort Jones, Dunsmuir, McCloud, Grenada, Happy Camp, Hornbrook, Butte Valley, Big Springs, Gazelle, Greenview, Hilt, Macdoel, Tennant.',
    'Butte County': 'Chico, Oroville, Paradise, Gridley, Biggs, Durham, Magalia, Palermo, Thermalito, Bangor, Berry Creek, Butte Creek Canyon, Butte Meadows, Cherokee, Clipper Mills, Cohasset, Concow, Forbestown, Forest Ranch, Honcut, Hurleton, Richvale, Stirling City, Yankee Hill.',
}


def link(path=''):
    return BASE + path.lstrip('/')


def norm(t):
    return re.sub(r'\s+', ' ', (t or '').replace('\xa0', ' ')).strip()


ICONS = (ROOT / 'site-source/icons.svg').read_text()

SITUATIONS = [
    ('inherited', 'violet', 'I inherited it', 'Estate', 'An inherited house', 'A family property, belongings to sort, and decisions to make. Often from out of the area.'),
    ('condition', 'gold', 'It needs a lot of work', 'Condition', 'More repairs than you want', 'Fire or water damage, an aging roof, or a house that needs more work than you want to take on.'),
    ('deadline', 'crimson', 'I’m up against a deadline', 'Time pressure', 'A deadline to work around', 'Late payments, foreclosure, a move, or another reason time matters.'),
    ('rental', 'brand', 'It’s a rental I’m done with', 'Landlord', 'Ready to leave a rental behind', 'Tenants, maintenance, and a property you’re ready to let go.'),
    ('moving', 'emerald', 'I’m moving by a date', 'Timeline', 'A change in your life', 'Relocating, downsizing, or figuring out your next chapter.'),
    ('comparing', 'slate-l', 'Just weighing it up', 'Comparing', 'Just exploring your options', 'Compare a direct sale with listing, side by side, without committing to anything.'),
]
QUIZ = link('get-a-cash-offer-today/')

# Verbatim Google reviews shown on ibuyredding.com (all 5 stars, January 2026).
REVIEWS = [
    ('Great experience working with Oscar. Not only did he make the process seamless he was also very patient and caring! Would recommend him every time!', 'Yesenia Melendez', 'Google review'),
    ('Oscar made the entire process incredibly easy. Communication was clear, timelines were met, and everything went exactly as promised. I couldn’t have asked for a better experience. Will be recommending to all my friends and family!', 'Hailey Cardin', 'Google review'),
    ('Fast, professional, and honest. Super easy process with no pressure. Highly recommend!', 'Yisvi Limon', 'Google review'),
]


def icon(name, cls=''):
    return f'<svg{" class=%s" % chr(34) + cls + chr(34) if cls else ""}><use href="#i-{name}"/></svg>'


def btn(label='See my selling options', href=QUIZ, cls='btn'):
    return f'<a class="{cls}" href="{href}">{label} {icon("arrow")}</a>'


def g_badge(cls=''):
    return (f'<a class="g-badge {cls}" href="{GOOGLE_URL}" target="_blank" rel="noopener">'
            f'<span class="g-logo" aria-hidden="true">G</span><b>{G_RATING}</b>'
            f'<span class="stars" style="--rating:{G_RATING}" aria-hidden="true">★★★★★</span>'
            f'<small>{G_COUNT} Google reviews</small></a>')


def chips(cls='chips'):
    return f'<div class="{cls}">' + ''.join(
        f'<a class="chip" style="--c:var(--{c})" href="{QUIZ}?s={k}#quiz"><i>{icon(k)}</i><span>{label}</span>{icon("arrow", "go")}</a>'
        for k, c, label, *_ in SITUATIONS) + '</div>'


def review_ticker():
    items = ''.join(f'<li class="rt-item google"><span class="rt-q" aria-hidden="true">“</span><q>{esc(q)}</q><span class="rt-by">{esc(n)} · {src}</span></li>' for q, n, src in REVIEWS * 2)
    return (f'<section class="review-ticker" aria-label="What sellers say about {BRAND}">'
            f'<a class="rt-badge" href="{GOOGLE_URL}" target="_blank" rel="noopener"><span class="g-logo" aria-hidden="true">G</span><b>{G_RATING}</b>'
            f'<span class="stars" style="--rating:{G_RATING}" aria-hidden="true">★★★★★</span><small>{G_COUNT} Google reviews</small></a>'
            f'<div class="rt-viewport"><ul class="rt-track">{items}</ul><ul class="rt-track" aria-hidden="true">{items}</ul></div></section>')


NAV = [('How it works', '#process'), (f'Meet {PERSON}', 'about/'), ('Inherited a house', 'sell-inherited-house-redding/'), ('Resources', 'blog/'), ('FAQ', 'faq/')]


def header():
    return (f'{ICONS}<a class="skip" href="#main">Skip to content</a>'
            f'<div class="preview-bar">Website preview <span>Forms are in demonstration mode · No inquiries are sent</span></div>'
            f'<header class="site-header" data-header><div class="container nav">'
            f'<a class="logo" href="{link()}"><img src="{link("img/logo.svg")}" alt="{BRAND} home" width="195" height="69"></a>'
            f'<nav id="navigation" aria-label="Main navigation">' + ''.join(f'<a href="{link(p) if not p.startswith("#") else link() + p}">{n}</a>' for n, p in NAV) + '</nav>'
            f'<div class="nav-right"><a class="nav-phone" href="{TEL}">{icon("phone")}<span><small>Call or text a local buyer</small>{PHONE}</span></a>'
            f'<a class="btn btn-sm" href="{QUIZ}">Get my cash offer</a>'
            f'<button class="menu-toggle" aria-expanded="false" aria-controls="navigation"><span></span><span></span><span class="sr">Menu</span></button></div>'
            f'</div></header>')


def closing():
    return (f'<section class="closing"><div class="closing-rings"><span></span><span></span><span></span></div>'
            f'<div class="container closing-inner reveal"><p class="eyebrow light">Get your cash offer today</p>'
            f'<h2>Let us help you navigate the home selling process hassle-free.</h2><p>A few questions. A real conversation. No obligation to sell.</p>'
            f'<div class="closing-actions">{btn(cls="btn btn-lg")}<a class="btn-ghost" href="{TEL}">{icon("phone")}{PHONE}</a></div>'
            f'<ul class="closing-checks"><li>{icon("check")}No repairs</li><li>{icon("check")}No fees or commissions</li><li>{icon("check")}No pressure</li></ul></div></section>')


def footer(sticky=True):
    s = (f'<div class="sticky-cta" data-sticky><a class="call" href="{TEL}" aria-label="Call {PHONE}">{icon("phone")}</a>{btn("Get my cash offer")}</div>' if sticky else '')
    return (f'<footer class="site-footer"><div class="container footer-grid">'
            f'<div class="footer-brand"><span class="logo-chip"><img src="{link("img/logo.svg")}" alt="{BRAND}" width="195" height="69"></span>'
            f'<p>Local cash home buyers.<br>{MARKET}.</p>{g_badge("dark")}</div>'
            f'<div><b>Explore</b><a href="{link("about/")}">About {BRAND}</a><a href="{link()}#process">How it works</a><a href="{link()}#compare">Traditional vs. {BRAND}</a><a href="{link()}#stories">Seller reviews</a><a href="{link("local-businesses-in-redding--ca/")}">Local businesses</a></div>'
            f'<div><b>For homeowners</b><a href="{link("blog/")}">Seller resources</a><a href="{link("sell-inherited-house-redding/")}">Inherited a house</a><a href="{link("faq/")}">Frequently asked questions</a><a href="{link("privacy-policy/")}">Privacy policy</a></div>'
            f'<div><b>We buy houses in</b>' + ''.join(f'<a href="{link()}#areas">{c}</a>' for c in COUNTIES) + '</div>'
            f'<div><b>Start a conversation</b><a class="footer-phone" href="{TEL}">{PHONE}</a><p>Call or text<br>{BRAND} is a brand of {OWNER}</p></div>'
            f'</div><div class="container footer-bottom">© 2026 {OWNER} <span>Website preview · No inquiries are sent from this preview.</span></div></footer>'
            f'{s}<script src="{link("assets/site.js?v=" + CSS_V)}" defer></script>')


def seo(title, description, path, kind='website', image=''):
    url = canonical(path)
    out = [f'<meta property="og:type" content="{kind}">', f'<meta property="og:title" content="{esc(title)}">',
           f'<meta property="og:description" content="{esc(description)}">', f'<meta property="og:url" content="{url}">',
           f'<meta property="og:site_name" content="{BRAND}">', '<meta name="twitter:card" content="summary_large_image">',
           f'<meta name="twitter:title" content="{esc(title)}">', f'<meta name="twitter:description" content="{esc(description)}">']
    if image:
        out += [f'<meta property="og:image" content="{esc(image)}">', f'<meta name="twitter:image" content="{esc(image)}">']
    return ''.join(out)


def canonical(path):
    p = path.strip('/')
    return f'{ORIGIN}/{p}' if p else f'{ORIGIN}/'


def page(title, body, path='', description='', head='', extra='', body_cls='', sticky=True):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="noindex,nofollow">'
            f'<link rel="canonical" href="{canonical(path)}">{head or seo(title, description, path)}<meta name="theme-color" content="#07090A">'
            f'<link rel="icon" href="{link("img/favicon.png")}"><link rel="apple-touch-icon" href="{link("img/favicon.png")}">'
            f'<link rel="preload" href="{link("assets/source-sans.woff2")}" as="font" type="font/woff2" crossorigin>'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bree+Serif&amp;display=swap">'
            f'<link rel="stylesheet" href="{link("assets/site.css?v=" + CSS_V)}"><script>document.documentElement.classList.add("js")</script>{extra}</head>'
            f'<body class="{body_cls}">{header()}{review_ticker()}<main id="main">{body}</main>{closing()}{footer(sticky)}</body></html>')


written = []


def write(path, content):
    p = ROOT / (path.strip('/') + '/index.html' if path.strip('/') else 'index.html')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    written.append(path)


def clean_html(frag):
    """Strip Durable layout, forms and scripts; keep headings, text, lists, links and images."""
    soup = BeautifulSoup(frag, 'html.parser')
    for e in soup.select('script,style,iframe,form,noscript,svg,button,input,textarea,select,label'):
        e.decompose()
    for e in soup.find_all(string=lambda t: isinstance(t, Comment)):
        e.extract()
    for e in soup.find_all(True):
        e.attrs = {k: v for k, v in e.attrs.items() if k in ['href', 'src', 'alt', 'title', 'colspan', 'rowspan']}
        if e.name == 'h1':
            e.name = 'h2'
        if e.name == 'img':
            if not e.get('src') or e['src'].startswith('data:'):
                e.decompose()
                continue
            e['loading'] = 'lazy'
            e['decoding'] = 'async'
        if e.name == 'a':
            href = e.get('href', '')
            if href.startswith('/') and not href.startswith('//'):
                e['href'] = link(href.split('?')[0].strip('/') + '/') if href.strip('/') else link()
            elif re.match(r'https?://(www\.)?ibuyredding\.com', href):
                rest = re.sub(r'https?://(www\.)?ibuyredding\.com/?', '', href).strip('/')
                e['href'] = link(rest + '/' if rest else '')
            else:
                e['target'] = '_blank'
                e['rel'] = 'noopener'
    for e in reversed(soup.find_all(['div', 'section', 'span', 'header', 'figure'])):
        e.unwrap()
    for e in soup.find_all(['p', 'li', 'h2', 'h3', 'h4']):
        if not e.get_text(strip=True) and not e.find('img'):
            e.decompose()
    return str(soup)


def durable_page(name):
    """Title, description and main sections (everything after the header) from a downloaded Durable page."""
    soup = BeautifulSoup((RAW / f'{name}.html').read_text(), 'html.parser')
    title = soup.title.get_text(strip=True)
    d = soup.find('meta', attrs={'name': 'description'})
    sections = [str(s) for s in soup.find('header').find_next_siblings('section')]
    return title, (d.get('content', '') if d else ''), ''.join(sections)


def aside_card():
    return (f'<aside class="side"><div class="side-card"><p class="side-title">What’s going on with the house?</p>{chips("chips chips-side")}'
            f'<a class="side-call" href="{TEL}">{icon("phone")}<span><small>Rather talk it through?</small>{PHONE}</span></a></div>'
            f'<div class="side-trust">{g_badge()}<p>{icon("pin")}Local to Redding &amp; Shasta County</p></div></aside>')


def page_hero(heading, crumb, lede='', meta_html='', extra=''):
    return (f'<section class="page-hero"><div class="hero-glow g1"></div><div class="hero-dots"></div><div class="container">'
            f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span>/</span>{crumb}</nav>'
            f'<h1>{esc(heading)}</h1>{lede}{meta_html}{extra}</div></section>')


def drop_first_heading(content, heading):
    """The page H1 lives in the hero, so drop an identical copy at the top of the body."""
    soup = BeautifulSoup(content, 'html.parser')
    first = soup.find(['h2', 'h3'])
    if first is not None and norm(first.get_text()).lower().rstrip('.') == norm(heading).lower().rstrip('.'):
        first.decompose()
    return str(soup)


manifest = []


def record(path, title, heading, description):
    manifest.append({'url': canonical(path), 'path': '/' + path.strip('/'), 'title': title, 'h1': heading, 'description': description,
                     'preview_url': PREVIEW + path.lstrip('/'), 'status': 'preserved path; v2 layout'})


# --------------------------------------------------------------------------------------------
# Standard pages
# --------------------------------------------------------------------------------------------
STANDARD = [
    ('about', 'about/', f'About {BRAND}', f'Meet {PERSON}'),
    ('faq', 'faq/', 'Frequently asked questions', 'FAQ'),
    ('sell-inherited-house-redding', 'sell-inherited-house-redding/', 'Inherited a House in Redding, CA? Sell It As-Is.', 'Inherited a house'),
    ('local-businesses-in-redding--ca', 'local-businesses-in-redding--ca/', 'Local Businesses in Redding, CA', 'Local businesses'),
    ('privacy-policy', 'privacy-policy/', 'Privacy policy', 'Privacy policy'),
]
for name, path, heading, crumb in STANDARD:
    title, desc, raw_html = durable_page(name)
    content = drop_first_heading(clean_html(raw_html), heading)
    if name == 'about':
        # Durable splits the brand name into its own heading; rejoin it with the sentence it starts.
        content = re.sub(r'(?:<h[23]>\s*' + BRAND + r'\s*</h[23]>\s*)?<h2>is a family owned', f'<h2>{BRAND} is a family owned', content, count=1)
        content = (f'<figure class="person-photo"><img src="{link("assets/oscar-manzo.jpg")}" alt="{PERSON_FULL}, {BRAND}" loading="lazy" width="700" height="1244"></figure>' + content)
    side = '' if name == 'privacy-policy' else aside_card()
    body = (page_hero(heading, f'<span>{esc(crumb)}</span>')
            + f'<div class="container article-grid{" no-side" if not side else ""}"><article class="prose">{content}</article>{side}</div>')
    write(path, page(title, body, path, desc, body_cls='inner'))
    record(path, title, heading, desc)

# --------------------------------------------------------------------------------------------
# Blog: all posts from the site's own page data
# --------------------------------------------------------------------------------------------
posts = sorted(json.loads((RAW / 'posts.json').read_text()), key=lambda p: p.get('publishedAt') or '', reverse=True)
colors = ['violet', 'gold', 'crimson', 'brand-d', 'emerald', 'slate']


def post_desc(p):
    t = norm(BeautifulSoup(p.get('content') or '', 'html.parser').get_text(' '))
    return (t[:155].rsplit(' ', 1)[0] + '…') if len(t) > 158 else t


def post_date(p):
    try:
        return datetime.fromisoformat(p['publishedAt'].replace('Z', '+00:00')).strftime('%B %-d, %Y')
    except Exception:
        return ''


for i, p in enumerate(posts):
    path = f'blog/{p["slug"]}/'
    desc = post_desc(p)
    a = p.get('Author') or {}
    author = norm(f'{a.get("firstName", "")} {a.get("lastName", "")}') if isinstance(a, dict) else ''
    img = (p.get('Image') or {}).get('url', '')
    meta_html = '<div class="post-meta">' + (f'<span>{icon("user")}By {esc(author)}</span>' if author else '') + f'<span>{icon("calendar")}{post_date(p)}</span></div>'
    content = drop_first_heading(clean_html(p.get('content') or ''), p['title'])
    if img:
        content = f'<figure class="post-cover"><img src="{esc(img)}" alt="{esc((p.get("Image") or {}).get("description", ""))}" loading="lazy" decoding="async"></figure>' + content
    picks = [posts[(i + k) % len(posts)] for k in (1, 2, 3)]
    related = ('<section class="section related"><div class="container"><div class="head"><p class="eyebrow">Keep reading</p><h2>More seller resources</h2></div><div class="resource-grid">'
               + ''.join(f'<a class="resource-card" style="--c:var(--{colors[(i + k) % 6]})" href="{link("blog/" + r["slug"] + "/")}"><i>{icon("book")}</i><h3>{esc(r["title"])}</h3><p>{esc(post_desc(r))}</p><span class="more">Read article {icon("arrow")}</span></a>'
                         for k, r in enumerate(picks)) + '</div></div></section>')
    body = (page_hero(p['title'], f'<a href="{link("blog/")}">Seller resources</a>', meta_html=meta_html)
            + f'<div class="container article-grid"><article class="prose">{content}</article>{aside_card()}</div>' + related)
    write(path, page(p['title'], body, path, desc, seo(p['title'], desc, path, 'article', img), body_cls='inner'))
    record(path, p['title'], p['title'], desc)

btitle, bdesc, _ = durable_page('blog')
bheading = 'Tips for Selling a Home: What You Need to Know'
cards = ''.join(
    f'<a class="resource-card" style="--c:var(--{colors[k % 6]})" href="{link("blog/" + r["slug"] + "/")}"><i>{icon("book")}</i>'
    f'<span class="date">{post_date(r)}</span><h2>{esc(r["title"])}</h2><p>{esc(post_desc(r))}</p><span class="more">Read article {icon("arrow")}</span></a>'
    for k, r in enumerate(posts))
blog_body = (page_hero(bheading, '<span>Seller resources</span>',
                       f'<p class="page-lede big">Articles from {BRAND} on selling a house in Redding and Shasta County: inherited properties, repairs, market updates and your options.</p>',
                       extra='<div class="search"><label class="sr" for="resource-search">Find a resource</label>' + icon('book') +
                             f'<input type="search" id="resource-search" placeholder="Search {len(posts)} articles: try inherited, repairs, or Shasta Lake"></div>')
             + f'<div class="container resource-grid library">{cards}</div><p id="no-results" hidden class="container no-results">No matching articles. Try a different word.</p>')
write('blog/', page(btitle, blog_body, 'blog/', bdesc, body_cls='inner'))
record('blog/', btitle, bheading, bdesc)

# --------------------------------------------------------------------------------------------
# Assessment (the proven multi-situation funnel, isolated in an iframe) and its page
# --------------------------------------------------------------------------------------------
original = (ROOT / 'site-source/funnel-original.html').read_text()
style = re.search(r'<style>(.*?)</style>', original, re.S).group(1)
quiz = original[original.index('<section id="quiz">'):]
quiz = quiz[:quiz.index('</section>') + 10]
scripts = '\n'.join(re.findall(r'<script>(.*?)</script>', original, re.S))
scripts = scripts.replace('var ASSISTANT_ON = true', 'var ASSISTANT_ON = false').replace('const ASSISTANT_ON = true', 'const ASSISTANT_ON = false')
scripts = scripts.replace('https://www.homebuyerswi.com/privacy/', link('privacy-policy/'))
scripts = re.sub(r'function doneHtml\(\)\{.*?\n\}', '''function doneHtml(){return '<div class="fade done"><div class="tick">✓</div><h3>You’ve reached the end of the preview.</h3><p>Your answers stayed in this browser. No inquiry was sent and no callback has been requested.</p><p>In the live site, this step will confirm that IBuyRedding has actually received your inquiry.</p><a class="btn btn-line" href="../blog/" target="_top">Explore seller resources</a></div>';}''', scripts, flags=re.S)
scripts = scripts.replace('label="Sent"', 'label="Preview complete"')
scripts = scripts.replace('if(consent&&!consent.checked) problems.push("the tick box so we are allowed to contact you");', '')
scripts = scripts.replace('consent:{given:true,', 'consent:{given:!!(consent && consent.checked),')
scripts = scripts.replace('I agree to receive text messages', '(Optional) I agree to receive text messages')
scripts = scripts.replace('if(window.console) console.info("[lead payload]", lead);', '/* Preview only: no transmission, PII logging or conversion event. */')
scripts = re.sub(r'function getGuide\(e\)\{[^\n]+\}', 'function getGuide(e){ e.preventDefault(); top.location.href="../blog/"; return false; }', scripts)
scripts = scripts.replace('"Send Me The Guide":"Send This And Call Me Back"', '"Finish Preview":"Finish Preview"')
scripts = scripts.replace('No obligation. Not a listing agreement. Not a commitment to sell.', 'Preview only. Please use made-up contact details. No information is sent.')
# Rebrand the funnel for IBuyRedding: market, service area, phone and price bands.
FUNNEL_SUBS = [
    ('opts:["Milwaukee","Waukesha","New Berlin","Wauwatosa","Racine","Greenfield","Elsewhere in Wisconsin","Outside Wisconsin"]',
     'opts:["Redding","Anderson","Shasta Lake","Red Bluff","Chico","Elsewhere in Shasta, Tehama, Siskiyou or Butte County","Outside those four counties"]'),
    ('a.location==="Outside Wisconsin"', 'a.location==="Outside those four counties"'),
    ('S.answers.location==="Elsewhere in Wisconsin"', 'S.answers.location==="Elsewhere in Shasta, Tehama, Siskiyou or Butte County"'),
    ('opts:["Under $100,000","$100,000 to $175,000","$175,000 to $250,000","$250,000 to $400,000","Over $400,000","I would rather not say"]',
     'opts:["Under $200,000","$200,000 to $300,000","$300,000 to $400,000","$400,000 to $550,000","Over $550,000","I would rather not say"]'),
    ('That property is outside Wisconsin, so it is outside what we do.', 'That property is outside the four counties we buy in, so it is outside what we do.'),
    ('We buy in Milwaukee and the surrounding communities', 'We buy in Shasta, Tehama, Siskiyou and Butte counties'),
    ('We buy across Milwaukee and the surrounding communities', 'We buy across Shasta, Tehama, Siskiyou and Butte counties'),
    ('Kustom buys in Wisconsin', 'IBuyRedding buys in Northern California'),
    ('Milwaukee code violations', 'code violations'), ('a Milwaukee duplex', 'a duplex'),
    ('on a house of this age around Milwaukee it is close to standard', 'on an older house around Redding it is close to standard'),
    ('Milwaukee and southeastern Wisconsin', 'Redding and Northern California'),
    ('Kustom Property Solutions', BRAND), ('Kustom', BRAND),
    ('(262) 432-1760', PHONE), ('tel:+12624321760', TEL),
    ('https://www.homebuyerswi.com/', ORIGIN + '/'), ('Milwaukee, Wisconsin', 'Redding, California'),
    ('"kustom-height"', '"funnel-height"'),
    ("We buy across Milwaukee and the '", "We buy across Shasta, Tehama, Siskiyou and Butte counties '"),
    ("+'surrounding communities and we will confirm", "+'and we will confirm"),
    ('Consent wording copied VERBATIM from the two live forms on\n     www.homebuyerswi.com (read 2026-09-10), so this funnel makes no\n     claim the client\'s own site does not already make.',
     'Consent wording carried over from the REI template default. IBuyRedding\'s\n     own SMS consent wording has not been confirmed yet.'),
    ('Values verified from www.homebuyerswi.com on 2026-09-10.', 'Values read from ibuyredding.com on 2026-11-16.'),
    ('homebuyerswi.com', 'ibuyredding.com'),
]
for a, b in FUNNEL_SUBS:
    scripts = scripts.replace(a, b)
    quiz = quiz.replace(a, b)
quiz = quiz.replace('Most people are in more than one situation at once.', 'What’s happening with your house?')
quiz = re.sub(r'<p class="sec-p">.*?</p>', '<p class="sec-p">Choose everything that applies. We’ll ask a few relevant questions so the next conversation starts in the right place.</p><p class="preview-note">This is a demonstration. Please use made-up details. No inquiry will be sent.</p>', quiz, count=1, flags=re.S)
leftover = sorted(set(re.findall(r'Kustom|Milwaukee|Wisconsin|homebuyerswi|262\) 432', scripts + quiz)))
assert not leftover, f'Funnel still mentions: {leftover}'
quiz_v2 = (ROOT / 'site-source/quiz-v2.css').read_text()
funnel_doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
              f'<title>Explore your selling options | {BRAND}</title>'
              f'<style>@font-face{{font-family:"Source Sans 3";src:url("{link("assets/source-sans.woff2")}") format("woff2");font-weight:200 900;font-display:swap}}'
              + style + '\n' + quiz_v2 + '</style></head><body>' + quiz + '<script>' + scripts + '</script>'
              '<script>new ResizeObserver(()=>{parent.postMessage({type:"funnel-height",height:document.body.scrollHeight},location.origin)}).observe(document.body);</script></body></html>')
write('assessment/', funnel_doc)

q_title = f'Get a Free & Fast Cash Offer | {BRAND}'
q_desc = 'Get cash for your home, fast and hassle-free. No obligation offer. We buy houses as-is in Redding and Northern California, with no fees and no commission.'
quiz_hero = (f'<section class="page-hero quiz-hero"><div class="hero-glow g1"></div><div class="hero-dots"></div><div class="container">'
             f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span>/</span><span>Get a cash offer</span></nav>'
             f'<h1>Get a Free &amp; Fast Cash Offer</h1>'
             f'<div class="quiz-trust"><span>{icon("check")}About two minutes</span><span>{icon("check")}No obligation</span><a href="{TEL}">{icon("phone")}{PHONE}</a>{g_badge("dark")}</div></div></section>')
quiz_frame = (f'<section class="quiz-wrap" id="quiz"><div class="container"><div class="quiz-card"><iframe id="assessment-frame" title="Property situation assessment" src="{link("assessment/")}" loading="eager"></iframe></div></div></section>')
quiz_more = (f'<section class="section quiz-more"><div class="container article-grid no-side"><article class="prose"><p><strong>#1 Most Trusted Cash Home Buyer in Redding Ca!</strong></p>'
             f'<p>Sell your house as-is. Pay No Fees. On your schedule. Tell us about the property and we’ll send you a “no strings attached” offer!</p><p>Call or Text <a href="{TEL}">{PHONE}</a></p></article></div></section>')
frame_js = '<script>addEventListener("DOMContentLoaded",()=>{const f=document.getElementById("assessment-frame");f.src+="?"+new URLSearchParams(location.search).toString();addEventListener("message",e=>{if(e.origin===location.origin&&e.source===f.contentWindow&&e.data?.type==="funnel-height"&&Number.isFinite(e.data.height))f.style.height=Math.max(520,e.data.height+10)+"px";});});</script>'
write('get-a-cash-offer-today/', page(q_title, quiz_hero + quiz_frame + quiz_more, 'get-a-cash-offer-today/', q_desc, extra=frame_js, body_cls='inner quiz-page', sticky=False))

# --------------------------------------------------------------------------------------------
# Homepage: v2 design built around the original homepage's headings and copy
# --------------------------------------------------------------------------------------------
h_title, h_desc, _ = durable_page('home')
reason_lists = {
    'Any Reason': ('violet', 'inherited', ['<a href="' + link('sell-inherited-house-redding/') + '">Inherited Property</a>', 'Relocation', 'Home Upgrades', 'Downsized Homes', 'Avoiding Foreclosure', 'Tired Landlords', 'Family Divorce', 'Avoiding Bankruptcies', 'Health or Medical Issues']),
    'Any Condition': ('gold', 'condition', ['Outdated or Old Houses', 'New Home Builds', 'Damaged by Storms', 'Fire or Water Damage', 'Damage by Termites', 'Full of Trash and/or Stuff', 'Majorly Needs Repairs', 'Tenants Rental Problems', 'Uncompleted Construction']),
    'Any Challenge': ('crimson', 'deadline', ['Financial Problems', 'Title Concerns', 'Violations of Code', 'Hoarder Properties', 'Low Home Equity', 'Large Tax Liens', 'Properties Out of Area', 'Family Issues', 'Mortgage Payments Late']),
}
tiles = ''.join(
    f'<a class="tile{" wide" if k in ("inherited", "comparing") else ""}{" dark" if k == "comparing" else ""} reveal" style="--c:var(--{"brand-d" if k == "rental" else c});--s:var(--{c.split("-")[0]}-soft)" href="{QUIZ}?s={k}#quiz">'
    f'<span class="tag">{tag}</span><i>{icon(k)}</i><h3>{esc(h)}</h3><p>{esc(d)}</p><span class="start">{"Compare my options" if k == "comparing" else "Start here"} {icon("arrow")}</span></a>'
    for k, c, _, tag, h, d in SITUATIONS)
reasons = ''.join(
    f'<div class="reason reveal" style="--c:var(--{c});--s:var(--{c}-soft)"><i>{icon(ic)}</i><h3>{t}</h3><ul class="checks">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul></div>'
    for t, (c, ic, items) in reason_lists.items())
county_html = ''.join(f'<p><strong>{c}:</strong> {towns}</p>' for c, towns in COUNTIES.items())
stories = ''.join(
    f'<figure class="story{" feature" if k == 1 else ""} reveal" style="--c:var(--{["violet", "emerald", "brand"][k]})"><span class="tag">Google review · 5 stars</span>'
    f'<blockquote>“{esc(q)}”</blockquote><figcaption><span class="initial" data-i="{n[0]}" aria-hidden="true"></span><b>{esc(n)}</b><small>{src}</small></figcaption></figure>'
    for k, (q, n, src) in enumerate([REVIEWS[1], REVIEWS[0], REVIEWS[2]]))

home = f'''
<section class="hero">
  <div class="hero-glow g1"></div><div class="hero-glow g2"></div><div class="hero-dots"></div>
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="pill"><span class="pulse"></span>Redding &amp; Shasta County · Local cash buyer</p>
      <h1><span class="h1-top">Sell Your Home Fast!</span> <span class="h1-bottom"><span class="mark">Redding CA<svg viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true"><path d="M3 17C60 7 180 3 297 12"/></svg></span></span></h1>
      <ul class="hero-points"><li>{icon("check")}Sell as-is</li><li>{icon("check")}Pay no fees</li><li>{icon("check")}On your schedule</li></ul>
      <p class="lede">#1 Most Trusted Cash Home Buyer in Redding Ca! Tell us what’s going on with the house and we’ll send you a “no strings attached” offer.</p>
      <div class="picker"><p class="picker-title">What’s going on with the house? <span>Pick one to start</span></p>{chips()}
        <p class="picker-foot">More than one fits? You can tell us about all of them. <a href="{TEL}">Or call or text {PHONE}</a></p></div>
    </div>
    <div class="hero-visual">
      <div class="arch-ring"></div>
      <figure class="arch"><img src="{link("assets/oscar-manzo.jpg")}" alt="{PERSON_FULL} of {BRAND}" width="788" height="1400" fetchpriority="high"></figure>
      <div class="float-card hello"><span class="avatar-dot"></span><div><small>Your local buyer</small><b>Hi, I’m {PERSON}.</b></div></div>
      <blockquote class="float-card quote"><p>“Oscar made the entire process incredibly easy.”</p><footer>Hailey Cardin · Google review</footer></blockquote>
      {g_badge("float-card rating")}
    </div>
  </div>
</section>

<section class="benefits"><div class="container"><ul class="benefit-card">
  <li style="--c:var(--gold)"><i>{icon("hammer")}</i><div><b>Sell as-is</b><span>No repairs needed</span></div></li>
  <li style="--c:var(--brand)"><i>{icon("cash")}</i><div><b>No fees or commissions</b><span>No closing costs</span></div></li>
  <li style="--c:var(--emerald)"><i>{icon("calendar")}</i><div><b>Close quickly</b><span>As fast as 10 days, or your schedule</span></div></li>
  <li style="--c:var(--violet)"><i>{icon("hand")}</i><div><b>No pressure</b><span>No obligation to accept</span></div></li>
</ul></div></section>

<section class="section intro">
  <div class="container intro-grid">
    <div class="intro-copy reveal">
      <p class="eyebrow">Conveniences</p>
      <h2>Get a Free &amp; Fast Cash Offer</h2>
      <p class="big">Sell your house as-is. Pay No Fees. On your schedule. Call or Text <a href="{TEL}">{PHONE}</a>.</p>
      <p><strong>Selling Fast and Easy.</strong> We buy homes quickly in Shasta County, CA, offering fast cash solutions for distressed sellers. Avoid lengthy processes and sell your home with ease.</p>
      <p><strong>No Real Estate Fees or Commissions.</strong> We buy homes directly, so you don’t pay any real estate fees or commissions. This saves you money and time, making the selling process stress-free and simple.</p>
      <div class="callout" style="--c:var(--brand)"><h3>Sell in As-is Condition with No Repairs</h3><p>We buy homes in their current condition. Avoid repair costs and sell your property without extra hassle or delay. Get convenience and peace of mind in the selling process.</p></div>
    </div>
    <div class="intro-visual reveal">
      <figure class="tilt"><img src="{link("assets/house-blue.jpg")}" alt="A house purchased by {BRAND} in Redding, CA" loading="lazy" decoding="async"></figure>
      <div class="intro-badge">{icon("pin")}<span><b>Redding</b> and Northern California</span></div>
    </div>
  </div>
</section>

<section class="section situations">
  <div class="container">
    <div class="head reveal"><p class="eyebrow">Start with your situation</p><h2>There’s more to a house <br class="d">than its address.</h2>
      <p>Every situation asks different questions, so every one gets its own path. Choose what brought you here.</p></div>
    <div class="bento">{tiles}</div>
  </div>
</section>

<section class="section mke" id="areas">
  <div class="mke-glow"></div>
  <div class="container mke-grid">
    <div class="mke-copy reveal">
      <p class="eyebrow light">Where do we buy?</p>
      <h2>We Purchase in Shasta County, Tehama County, Siskiyou County &amp; Butte County!</h2>
      <p>{BRAND} is a family owned and operated real estate investment firm proudly serving Northern California. Our process allows us to deliver offers quickly, often within 7-14 days, whatever the condition of the home.</p>
      <div class="stats">
        <div style="--c:var(--amber)"><b data-count="4" data-dec="0" data-suffix="">4</b><span>Northern California counties we buy in</span></div>
        <div style="--c:#5CCBF0"><b data-count="10" data-dec="0" data-suffix=" days">10 days</b><span>Close in as fast as 10 days, or on your schedule</span></div>
        <div style="--c:#FF7A80"><b data-count="0" data-dec="0" data-suffix="">0</b><span>Fees, commissions or closing costs for you</span></div>
      </div>
    </div>
    <div class="mke-visual reveal">
      <figure><img src="{link("assets/house-street.jpg")}" alt="Homes in Redding, CA" loading="lazy" decoding="async"></figure>
    </div>
  </div>
  <div class="container problems reveal">
    <div class="problems-card"><p class="problems-title"><strong>Communities we serve</strong></p>{county_html}</div>
    <div class="problems-side"><p>If you need to sell your house, we’d like to make you a fair cash offer and close on it when you’re ready to sell.</p>
      <p class="areas-title">{icon("pin")}We buy houses in:</p>
      <div class="areas dark">''' + ''.join(f'<span>{c}</span>' for c in COUNTIES) + f'''</div></div>
  </div>
</section>

<section class="section reasons">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">Any house. Any story.</p><h2>We buy houses for <span class="grad">any reason, any condition, any challenge.</span></h2></div>
    <div class="reason-grid">{reasons}</div>
    <div class="reason-foot reveal"><p>Get Your Cash Offer Today. Let us help you navigate through the home selling process hassle-free.</p><p class="call-line">Call or Text {PHONE}</p></div>
  </div>
</section>

<section class="section compare" id="compare">
  <div class="container">
    <div class="head reveal"><p class="eyebrow">Side by side</p><h2>Traditional Vs {BRAND}</h2><p>See how selling directly to {BRAND} compares with the traditional real estate sale process.</p></div>
    <div class="compare-grid">
      <div class="compare-card cash reveal"><span class="ribbon">{BRAND}</span><i>{icon("cash")}</i><h3>Selling to {BRAND}</h3><ul class="checks">
<li><strong>No Fees:</strong><br>Save your money for your next move and close confidently without shelling out any cent with our reliable method.</li>
<li><strong>Highest Price:</strong><br>Maximize your home’s off-market price and get the most out of your property regardless of its condition.</li>
<li><strong>Sell As-is:</strong><br>Forget about sprucing up your property for showings and secure a buyer with us.</li>
<li><strong>Close Quickly:</strong><br>Close confidently in as fast as 10 days or according to your specific schedule.</li>
<li><strong>No Closing Costs:</strong><br>You get cash and don’t have to spend anything once you close.</li>
</ul></div>
      <div class="compare-card trad reveal"><i>{icon("calendar")}</i><h3>Traditional Real Estate Sale Process</h3><ul class="crosses">
<li><strong>Extra Fees:</strong><br>You may need to shell out certain percentages of the purchase price before you can even close.</li>
<li><strong>Unsure Buyers:</strong><br>People can haggle or change their minds later on, leaving you uncertain and unconfident about whether you’ll close.</li>
<li><strong>Cleaning Up:</strong><br>Selling a property involves making it attractive for potential buyers, which may require you to invest in repairs.</li>
<li><strong>Open Houses:</strong><br>You would need to schedule showings and invite people before you can sell your house.</li>
<li><strong>Long Timeline:</strong><br>Expect to wait at least two months (if you’re lucky) before you can sell your property completely.</li>
</ul></div>
    </div>
  </div>
</section>

<section class="section process" id="process">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">Steps</p><h2>Three steps. <span class="grad">Room to breathe.</span></h2><p>No fixing up for photos. No weekend showings. Just a conversation about the property and a plan that fits.</p></div>
    <ol class="timeline reveal">
      <li style="--c:var(--brand)"><span class="num">1</span><h3>Connect With Us</h3><p>We help distressed home sellers in Shasta County, CA. Reach out to our team for a smooth cash sale process. We offer fair prices and handle all the details.</p></li>
      <li style="--c:var(--violet)"><span class="num">2</span><h3>Get A Cash Offer</h3><p>We help homeowners sell their properties quickly and with ease, especially those facing distressing situations. Contact us to receive a fair cash offer.</p></li>
      <li style="--c:var(--act)"><span class="num">3</span><h3>Cash Out On Your Home</h3><p>Sell your house quickly and easily without the hassle of repairs or delays. We provide convenience for distressed home sellers.</p></li>
    </ol>
    <div class="differently reveal">
      <figure><img src="{link("assets/kitchen-renovated.jpg")}" alt="A kitchen renovated by {BRAND}" loading="lazy" decoding="async"></figure>
      <div><h3>Whatever the condition, we are ready to provide an offer.</h3><p>Our process allows us to deliver offers quickly, often within 7-14 days, and whatever the condition of the home—from tenant issues to fire damage and beyond—we are ready to provide an offer. <strong>There is absolutely no pressure to accept the offer</strong>; clients can take the time to review their options without any commitment.</p><p>We will have a conversation with you about your property and ask you a few questions about it. If it meets our criteria, we will present you with a cash offer. If the offer works for you, you can accept it, and we will open Escrow. Once Escrow closes, the proceeds get wired directly into your bank account. (<a href="{link("faq/")}">Read our FAQ →</a>)</p></div>
    </div>
  </div>
</section>

<section class="section riz" id="oscar">
  <div class="container riz-grid">
    <div class="riz-visual reveal"><div class="blob"></div>
      <figure class="lake"><img src="{link("assets/house-fence.jpg")}" alt="A Redding home purchased by {BRAND}" width="1300" height="975" loading="lazy"></figure>
      <div class="riz-badge"><img src="{link("assets/oscar-manzo.jpg")}" alt="{PERSON_FULL}" loading="lazy"><div><b>{PERSON_FULL}</b><span>{BRAND}</span></div></div></div>
    <div class="riz-copy reveal">
      <p class="eyebrow">Meet your local buyer</p>
      <h2>It starts with a conversation. <em>With {PERSON}.</em></h2>
      <p class="kicker">{BRAND} is a family owned and operated real estate investment firm proudly serving Northern California.</p>
      <p>We specialize in providing cash offers for homes in Northern California and pride ourselves on our relationships with local homeowners as well as the Realtor community. We understand that every customer is unique, so we strive to always be fair and honest with our clients.</p>
      <p class="areas-title">{icon("pin")}We buy houses throughout Northern California</p>
      <div class="areas">''' + ''.join(f'<a href="#areas">{c}</a>' for c in COUNTIES) + f'''</div>
      <a class="text-link" href="{link("about/")}">Get to know {BRAND} {icon("arrow")}</a>
    </div>
  </div>
</section>

<section class="section stories" id="stories">
  <div class="container">
    <div class="head stories-head reveal"><div><p class="eyebrow">Google reviews</p><h2>People who were where <br class="d">you are now.</h2><p>In their own words, from {BRAND}’s Google reviews.</p></div>{g_badge("big")}</div>
    <div class="story-grid">{stories}</div>
    <a class="text-link reveal" href="{GOOGLE_URL}" target="_blank" rel="noopener">Read all Google reviews {icon("arrow")}</a>
  </div>
</section>

<section class="section faqs" id="faq">
  <div class="container faq-grid">
    <div class="head reveal"><p class="eyebrow">Good questions. Straight answers.</p><h2>Before you take the next step.</h2><a class="text-link" href="{link("faq/")}">All frequently asked questions {icon("arrow")}</a></div>
    <div class="faq-list reveal">
      <details style="--c:var(--gold)"><summary>Do I need to repair or clean out the house?</summary><p>No. We buy homes in their current condition, from tenant issues to fire damage and beyond. Tell us about the condition and anything you’d prefer to leave behind.</p></details>
      <details style="--c:var(--violet)"><summary>Is there any obligation to accept an offer?</summary><p>No. There is absolutely no pressure to accept the offer; you can take the time to review your options without any commitment.</p></details>
      <details style="--c:var(--emerald)"><summary>How quickly could we close?</summary><p>In as fast as 10 days, or according to your specific schedule, where the property and title allow. Offers often come within 7-14 days.</p></details>
      <details style="--c:var(--brand)"><summary>How do I get paid?</summary><p>If the offer works for you, you accept it and we open Escrow. Once Escrow closes, the proceeds get wired directly into your bank account.</p></details>
    </div>
  </div>
</section>'''
write('', page(h_title, home, '', h_desc, body_cls='home'))
record('', h_title, 'Sell Your Home Fast! Redding CA', h_desc)

# --------------------------------------------------------------------------------------------
# Migration files
# --------------------------------------------------------------------------------------------
(ROOT / 'migration').mkdir(exist_ok=True)
(ROOT / 'migration/url-inventory.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
with (ROOT / 'migration/url-map.csv').open('w') as f:
    w = csv.writer(f)
    w.writerow(['Existing URL', 'Planned production URL', 'Preview URL', 'Action'])
    w.writerows((m['url'], m['url'], m['preview_url'], 'Keep existing path') for m in manifest)
(ROOT / 'migration/sitemap-production.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                                       + ''.join(f'  <url><loc>{esc(m["url"])}</loc></url>\n' for m in manifest) + '</urlset>\n')
(ROOT / '.nojekyll').touch()
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n# Every preview page has a noindex,nofollow meta directive.\n')
print(f'Built {len(written)} pages ({len(posts)} blog articles), homepage and integrated assessment.')
