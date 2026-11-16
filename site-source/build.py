"""Generate the IBuyRedding replacement website preview from the REI template default.

Inputs (snapshot of the public ibuyredding.com site, read 16 November 2026, kept outside this repo):
  home.html, about.html, faq.html, sell-inherited-house-redding.html, local-businesses-in-redding--ca.html,
  privacy-policy.html and posts.json (all 145 blog posts from the site's own page data),
The lead form is contact-first (step 1) with optional situation questions (step 2).

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
CSS_V = '20261117a'

BRAND = 'IBuyRedding'
# Link preview (texted or shared URLs): the official logo on black, 1200x630. Switch to ORIGIN at launch.
OG_IMAGE = PREVIEW + 'img/og-image.png'
HOME_TITLE = 'IBuyRedding | Sell Your House Fast for Cash in Redding, CA'
# Oscar is sending the YouTube link for the homepage video. Until then the preview shows a placeholder.
YOUTUBE_ID = ''
# SMS consent supplied by the client (16 November 2026). Optional, unchecked, not required to submit.
# Covers only inquiry and appointment messages; promotional texting needs separate consent.
SMS_CONSENT = ('I agree to receive non-marketing text messages from Manzo Capital LLC, operating as IBuyRedding, about my property inquiry, '
               'including follow-ups and appointment confirmations. Message frequency varies. Message and data rates may apply. '
               'Reply STOP to unsubscribe or HELP for assistance. Consent is not required to submit an inquiry or use our services.')
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


def btn(label='Get my cash offer', href=QUIZ, cls='btn'):
    return f'<a class="{cls}" href="{href}">{label} {icon("arrow")}</a>'


def lead_form(uid='offer', tag='h2'):
    """Contact details first (step 1), then optional situation questions (step 2).
    Preview mode: nothing is sent. At launch, step 1 posts the lead to GHL and step 2 updates it."""
    f = lambda n: f'{uid}-{n}'
    opts = ''.join(f'<label class="lf-opt"><input type="checkbox" name="situation" value="{k}"><span>{label}</span></label>' for k, _, label, *_ in SITUATIONS)
    terms = (f'<a href="{link("sms-terms/")}" target="_blank" rel="noopener">SMS Terms</a> · '
             f'<a href="{link("privacy-policy/")}" target="_blank" rel="noopener">Privacy Policy</a>')
    return (f'<form class="lead-card" id="{uid}" data-lead-form novalidate aria-label="Get your free cash offer">'
            f'<div class="lf-step" data-step="1">'
            f'<{tag} class="lf-title">Get Your Free Cash Offer</{tag}><p class="lf-sub">60 seconds. No obligation.</p>'
            f'<div class="lf-row"><div class="lf-field"><label for="{f("first")}">First Name</label><input id="{f("first")}" name="firstName" autocomplete="given-name" required></div>'
            f'<div class="lf-field"><label for="{f("last")}">Last Name</label><input id="{f("last")}" name="lastName" autocomplete="family-name" required></div></div>'
            f'<div class="lf-field"><label for="{f("address")}">Property Address</label><input id="{f("address")}" name="address" autocomplete="street-address" placeholder="123 Main St, Redding, CA" required></div>'
            f'<div class="lf-field"><label for="{f("phone")}">Phone</label><input id="{f("phone")}" name="phone" type="tel" inputmode="tel" autocomplete="tel" required></div>'
            f'<label class="lf-consent"><input type="checkbox" name="smsConsent" value="yes"><span><b>Optional.</b> {SMS_CONSENT} {terms}</span></label>'
            f'<div class="lf-field"><label for="{f("email")}">Email <span class="lf-opt-tag">(optional)</span></label><input id="{f("email")}" name="email" type="email" autocomplete="email"></div>'
            f'<p class="lf-error" role="alert" hidden></p>'
            f'<button class="btn btn-block" type="submit">Get My Cash Offer {icon("arrow")}</button>'
            f'<p class="lf-privacy">{icon("lock")}<span>Your information is private. We never sell it or share it for marketing. <a href="{link("privacy-policy/")}">Privacy Policy</a></span></p>'
            f'</div>'
            f'<div class="lf-step" data-step="2" hidden tabindex="-1">'
            f'<p class="lf-ok">{icon("check")}<span>Thanks, <b data-first></b>. <small>Preview: nothing was sent.</small></span></p>'
            f'<p class="lf-title">What’s going on with the house?</p><p class="lf-sub">Optional. Choose any that apply so we can prepare for our conversation.</p>'
            f'<div class="lf-opts">{opts}</div>'
            f'<button class="btn btn-block" type="button" data-next>Continue {icon("arrow")}</button>'
            f'<button class="lf-skip" type="button" data-next>Skip this step</button>'
            f'</div>'
            f'<div class="lf-step" data-step="3" hidden tabindex="-1">'
            f'<p class="lf-ok">{icon("check")}<span>You’ve reached the end of the preview.</span></p>'
            f'<p class="lf-sub">Nothing was sent. On the live site, your details reach {BRAND} as soon as you press “Get My Cash Offer”, and this step confirms it.</p>'
            f'<a class="btn btn-block" href="{TEL}">{icon("phone")}Call {PHONE}</a>'
            f'</div></form>')


def rating_box(cls='rating-box'):
    return (f'<a class="{cls}" href="{GOOGLE_URL}" target="_blank" rel="noopener"><span class="g-logo" aria-hidden="true">G</span>'
            f'<b>{G_RATING}</b><span class="stars" style="--rating:{G_RATING}" role="img" aria-label="{G_RATING} out of 5 stars">★★★★★</span>'
            f'<small>{G_COUNT} Google reviews</small></a>')


def review_cards(items=REVIEWS):
    return ''.join(f'<figure class="review-card"><span class="stars" style="--rating:5" role="img" aria-label="5 out of 5 stars">★★★★★</span>'
                   f'<blockquote>“{esc(q)}”</blockquote><figcaption><span class="initial" aria-hidden="true">{n[0]}</span><b>{esc(n)}</b><small>{src}</small></figcaption></figure>'
                   for q, n, src in items)


def g_badge(cls=''):
    return (f'<a class="g-badge {cls}" href="{GOOGLE_URL}" target="_blank" rel="noopener">'
            f'<span class="g-logo" aria-hidden="true">G</span><b>{G_RATING}</b>'
            f'<span class="stars" style="--rating:{G_RATING}" aria-hidden="true">★★★★★</span>'
            f'<small>{G_COUNT} Google reviews</small></a>')


def chips(cls='chips'):
    return f'<div class="{cls}">' + ''.join(
        f'<a class="chip" style="--c:var(--{c})" href="{QUIZ}?s={k}#quiz"><i>{icon(k)}</i><span>{label}</span>{icon("arrow", "go")}</a>'
        for k, c, label, *_ in SITUATIONS) + '</div>'


NAV = [('Get my cash offer', QUIZ), ('How it works', '#process'), ('Reviews', '#stories'), (f'Meet {PERSON}', 'about/'),
       ('Inherited a house', 'sell-inherited-house-redding/'), ('Resources', 'blog/'), ('FAQ', 'faq/')]


def nav_href(p):
    return p if p.startswith(BASE) else (link() + p if p.startswith('#') else link(p))


def header():
    # Header is just: logo, phone button, menu.
    return (f'{ICONS}<a class="skip" href="#main">Skip to content</a>'
            f'<div class="preview-bar">Website preview <span>Forms are in demonstration mode · No inquiries are sent</span></div>'
            f'<header class="site-header" data-header><div class="container nav">'
            f'<a class="logo" href="{link()}"><img src="{link("img/logo.png")}" alt="{BRAND} home" width="176" height="76"></a>'
            f'<nav id="navigation" aria-label="Main navigation">' + ''.join(f'<a href="{nav_href(p)}">{n}</a>' for n, p in NAV) + '</nav>'
            f'<div class="nav-right"><a class="btn btn-sm btn-phone" href="{TEL}" aria-label="Call {PHONE}">{icon("phone")}<span class="num">{PHONE}</span><span class="lbl">Call</span></a>'
            f'<button class="menu-toggle" aria-expanded="false" aria-controls="navigation"><span></span><span></span><span class="sr">Menu</span></button></div>'
            f'</div></header>')


def closing():
    return (f'<section class="closing"><div class="container closing-inner reveal">'
            f'<h2>Get your cash offer today.</h2><p>Let us help you navigate the home selling process hassle-free. No obligation to sell.</p>'
            f'<div class="closing-actions">{btn(cls="btn btn-lg")}<a class="btn btn-lg" href="{TEL}">{icon("phone")}Call {PHONE}</a></div></div></section>')


def footer(sticky=True):
    s = (f'<div class="sticky-cta" data-sticky><a class="btn call" href="{TEL}" aria-label="Call {PHONE}">{icon("phone")}</a>{btn("Get my cash offer")}</div>' if sticky else '')
    return (f'<footer class="site-footer"><div class="container footer-grid">'
            f'<div class="footer-brand"><img class="footer-logo" src="{link("img/logo-white.png")}" alt="{BRAND}" width="190" height="82">'
            f'<p>Local cash home buyers.<br>{MARKET}.</p>{g_badge("dark")}</div>'
            f'<div><b>Explore</b><a href="{link("about/")}">About {BRAND}</a><a href="{link()}#process">How it works</a><a href="{link()}#compare">Traditional vs. {BRAND}</a><a href="{link()}#stories">Seller reviews</a><a href="{link("local-businesses-in-redding--ca/")}">Local businesses</a></div>'
            f'<div><b>For homeowners</b><a href="{link("blog/")}">Seller resources</a><a href="{link("sell-inherited-house-redding/")}">Inherited a house</a><a href="{link("faq/")}">Frequently asked questions</a><a href="{link("privacy-policy/")}">Privacy policy</a><a href="{link("sms-terms/")}">SMS terms</a></div>'
            f'<div><b>We buy houses in</b>' + ''.join(f'<a href="{link()}#areas">{c}</a>' for c in COUNTIES) + '</div>'
            f'<div><b>Start a conversation</b><a class="footer-phone" href="{TEL}">{PHONE}</a><p>{BRAND} is a brand of {OWNER}</p></div>'
            f'</div><div class="container footer-bottom">© 2026 {OWNER} <span>Website preview · No inquiries are sent from this preview.</span></div></footer>'
            f'{s}<script src="{link("assets/site.js?v=" + CSS_V)}" defer></script>')


def seo(title, description, path, kind='website', image=''):
    url = canonical(path)
    out = [f'<meta property="og:type" content="{kind}">', f'<meta property="og:title" content="{esc(title)}">',
           f'<meta property="og:description" content="{esc(description)}">', f'<meta property="og:url" content="{url}">',
           f'<meta property="og:site_name" content="{BRAND}">', '<meta name="twitter:card" content="summary_large_image">',
           f'<meta name="twitter:title" content="{esc(title)}">', f'<meta name="twitter:description" content="{esc(description)}">']
    img = image or OG_IMAGE
    out += [f'<meta property="og:image" content="{esc(img)}">', f'<meta name="twitter:image" content="{esc(img)}">']
    if not image:
        out += ['<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
                f'<meta property="og:image:alt" content="{BRAND} logo">']
    return ''.join(out)


def canonical(path):
    p = path.strip('/')
    return f'{ORIGIN}/{p}' if p else f'{ORIGIN}/'


def page(title, body, path='', description='', head='', extra='', body_cls='', sticky=True):
    out = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="noindex,nofollow">'
            f'<link rel="canonical" href="{canonical(path)}">{head or seo(title, description, path)}<meta name="theme-color" content="#0B1220">'
            f'<link rel="icon" type="image/png" sizes="48x48" href="{link("img/favicon-48.png")}"><link rel="icon" type="image/png" sizes="512x512" href="{link("img/favicon.png")}">'
            f'<link rel="apple-touch-icon" href="{link("img/apple-touch-icon.png")}">'
            f'<link rel="preload" href="{link("assets/source-sans.woff2")}" as="font" type="font/woff2" crossorigin>'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bree+Serif&amp;display=swap">'
            f'<link rel="stylesheet" href="{link("assets/site.css?v=" + CSS_V)}"><script>document.documentElement.classList.add("js")</script>{extra}</head>'
            f'<body class="{body_cls}">{header()}<main id="main">{body}</main>{closing()}{footer(sticky)}</body></html>')
    # On pages that carry the lead form, every "Get my cash offer" link goes straight to it.
    return out.replace(f'href="{QUIZ}"', 'href="#offer"') if 'data-lead-form' in body else out


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
    # Texting on the public number is not verified yet, so the site says "Call" only.
    return re.sub(r'\b([Cc])all or [Tt]ext\b', r'\1all', str(soup))


def durable_page(name):
    """Title, description and main sections (everything after the header) from a downloaded Durable page."""
    soup = BeautifulSoup((RAW / f'{name}.html').read_text(), 'html.parser')
    title = soup.title.get_text(strip=True)
    d = soup.find('meta', attrs={'name': 'description'})
    sections = [str(s) for s in soup.find('header').find_next_siblings('section')]
    return title, (d.get('content', '') if d else ''), ''.join(sections)


def aside_card():
    return (f'<aside class="side"><div class="side-card"><p class="side-title">Get your free cash offer</p><p class="side-sub">60 seconds. No obligation. Sell as-is and pay no fees.</p>'
            f'{btn("Get my cash offer", QUIZ + "#offer", "btn btn-block")}'
            f'<a class="side-call" href="{TEL}">{icon("phone")}<span><small>Rather talk it through?</small>{PHONE}</span></a></div>'
            f'<div class="side-trust">{g_badge()}<p>{icon("pin")}Local to Redding &amp; Shasta County</p></div></aside>')


def page_hero(heading, crumb, lede='', meta_html='', extra=''):
    return (f'<section class="page-hero"><div class="container">'
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
UPDATED = 'November 16, 2026'
PRIVACY_HTML = f'''<p><em>Last updated: {UPDATED}</em></p>
<p>{BRAND} is a brand owned and operated by {OWNER} (“{BRAND}”, “we”, “us”). This Privacy Policy explains what information we collect when you use this website or contact us, how we use it, and the choices you have.</p>
<h2>Information we collect</h2>
<ul><li><strong>Information you give us.</strong> When you complete our property questionnaire or contact us, we collect your name, phone number, email address, property address, and your answers about the property and your situation.</li>
<li><strong>Your text message choice.</strong> If you tick the optional SMS box, we record that you consented, when, and the page you consented on. If you reply STOP, we record that too.</li>
<li><strong>Website usage.</strong> Like most websites, we may collect browser type, IP address and pages visited to understand how the site is used.</li></ul>
<h2>How we use your information</h2>
<ul><li>To review your property, respond to your inquiry, and prepare and discuss an offer.</li>
<li>To call you, and, only if you consented, to send non-marketing text messages about your inquiry, including follow-ups and appointment confirmations.</li>
<li>To keep records of our conversations and transactions, and to meet legal obligations.</li></ul>
<p>We do not send promotional text messages unless you have given separate consent for them.</p>
<h2>Mobile numbers and SMS consent</h2>
<p><strong>We do not sell, rent or share your mobile phone number or your SMS consent with third parties or affiliates for their marketing or promotional purposes.</strong> Text messaging opt-in data and consent records are never shared with any third party, except with the service providers that deliver our messages on our behalf and are not permitted to use them for anything else.</p>
<p>See our <a href="{link("sms-terms/")}">SMS Terms</a> for how our text messages work, including how to opt out.</p>
<h2>When we share information</h2>
<p>We do not sell your personal information. We share it only:</p>
<ul><li>With service providers that help us run our business, such as our customer relationship management system, phone and text messaging providers, and website hosting, who may use it only to provide those services to us;</li>
<li>With title, escrow and other professionals needed to complete a transaction you choose to move forward with; and</li>
<li>When required by law, or to protect our rights or the safety of others.</li></ul>
<h2>Keeping your information secure</h2>
<p>We take reasonable steps to protect your information from unauthorized access, alteration, disclosure or destruction, and limit access to the people who need it to respond to you.</p>
<h2>Your choices</h2>
<ul><li>Reply <strong>STOP</strong> to any text message to stop receiving texts. Reply <strong>HELP</strong> for help.</li>
<li>Call us at <a href="{TEL}">{PHONE}</a> to ask what information we hold about you, or to ask us to correct or delete it. California residents may have additional rights under California law.</li></ul>
<h2>Changes to this policy</h2>
<p>We may update this policy from time to time. The date at the top shows when it last changed.</p>
<h2>Contact us</h2>
<p>{OWNER}, operating as {BRAND}<br>Phone: <a href="{TEL}">{PHONE}</a><br>Website: <a href="{link()}">ibuyredding.com</a></p>'''

SMS_TERMS_HTML = f'''<p><em>Last updated: {UPDATED}</em></p>
<h2>Program</h2>
<p>{OWNER}, operating as {BRAND}, sends non-marketing text messages about property inquiries to people who opt in on our website. Messages include follow-ups about your inquiry and appointment confirmations. We do not send promotional messages through this program.</p>
<h2>How to opt in</h2>
<p>You opt in by ticking the optional SMS box when you submit an inquiry on our website. Consent is not required to submit an inquiry or use our services.</p>
<h2>How to opt out (STOP)</h2>
<p>Reply <strong>STOP</strong> to any message at any time. You will receive one message confirming that you have been unsubscribed, and no further messages will be sent unless you opt in again.</p>
<h2>Help (HELP)</h2>
<p>Reply <strong>HELP</strong> to any message for assistance, or call us at <a href="{TEL}">{PHONE}</a>.</p>
<h2>Message frequency</h2>
<p>Message frequency varies depending on your inquiry and any appointments you schedule.</p>
<h2>Charges</h2>
<p>Message and data rates may apply, according to your mobile plan. {BRAND} does not charge for text messages.</p>
<h2>Carriers and delivery</h2>
<p>Mobile carriers are not liable for delayed or undelivered messages. Delivery depends on your carrier and device, and is not guaranteed.</p>
<h2>Privacy</h2>
<p>We do not sell, rent or share your mobile phone number or SMS consent with third parties or affiliates for marketing or promotional purposes. See our <a href="{link("privacy-policy/")}">Privacy Policy</a>.</p>
<h2>Support</h2>
<p>{OWNER}, operating as {BRAND}<br>Phone: <a href="{TEL}">{PHONE}</a></p>'''

for name, path, heading, crumb in STANDARD:
    title, desc, raw_html = durable_page(name)
    content = drop_first_heading(clean_html(raw_html), heading)
    if name == 'privacy-policy':
        content = PRIVACY_HTML
    if name == 'about':
        # Durable splits the brand name into its own heading; rejoin it with the sentence it starts.
        content = re.sub(r'(?:<h[23]>\s*' + BRAND + r'\s*</h[23]>\s*)?<h2>is a family owned', f'<h2>{BRAND} is a family owned', content, count=1)
        content = (f'<figure class="person-photo"><img src="{link("assets/oscar-manzo.jpg")}" alt="{PERSON_FULL}, {BRAND}" loading="lazy" width="700" height="1244"></figure>' + content)
    side = '' if name == 'privacy-policy' else aside_card()
    body = (page_hero(heading, f'<span>{esc(crumb)}</span>')
            + f'<div class="container article-grid{" no-side" if not side else ""}"><article class="prose">{content}</article>{side}</div>')
    write(path, page(title, body, path, desc, body_cls='inner'))
    record(path, title, heading, desc)

sms_title, sms_desc = f'SMS Terms | {BRAND}', f'How {BRAND} text messages about property inquiries work: frequency, charges, STOP and HELP, and support.'
write('sms-terms/', page(sms_title, page_hero('SMS Terms', '<span>SMS Terms</span>')
                         + f'<div class="container article-grid no-side"><article class="prose">{SMS_TERMS_HTML}</article></div>',
                         'sms-terms/', sms_desc, body_cls='inner'))
record('sms-terms/', sms_title, 'SMS Terms', sms_desc)

# --------------------------------------------------------------------------------------------
# Blog: all posts from the site's own page data
# --------------------------------------------------------------------------------------------
posts = sorted(json.loads((RAW / 'posts.json').read_text()), key=lambda p: p.get('publishedAt') or '', reverse=True)
colors = ['brand'] * 6  # one accent colour sitewide


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
# Get a cash offer: the same contact-first form as the homepage hero
# --------------------------------------------------------------------------------------------
q_title = f'Get a Free & Fast Cash Offer | {BRAND}'
q_desc = 'Get cash for your home, fast and hassle-free. No obligation offer. We buy houses as-is in Redding and Northern California, with no fees and no commission.'
q_body = (page_hero('Get a Free & Fast Cash Offer', '<span>Get a cash offer</span>',
                    '<p class="page-lede">Sell your house as-is. Pay no fees. On your schedule.</p>')
          + f'<section class="section offer-page"><div class="container offer-grid">{lead_form("offer")}'
          f'<div class="offer-side">{rating_box()}{review_cards(REVIEWS[:2])}'
          f'<a class="hero-call dark" href="{TEL}">{icon("phone")}<span>Rather talk it through? <b>Call {PHONE}</b></span></a></div></div></section>')
write('get-a-cash-offer-today/', page(q_title, q_body, 'get-a-cash-offer-today/', q_desc, body_cls='inner offer', sticky=False))
record('get-a-cash-offer-today/', q_title, 'Get a Free & Fast Cash Offer', q_desc)

# --------------------------------------------------------------------------------------------
# Homepage: contact-first hero form, then reviews and video, then the original homepage copy
# --------------------------------------------------------------------------------------------
_, h_desc, _ = durable_page('home')
h_title = HOME_TITLE
reason_lists = {
    'Any Reason': ('inherited', ['<a href="' + link('sell-inherited-house-redding/') + '">Inherited Property</a>', 'Relocation', 'Home Upgrades', 'Downsized Homes', 'Avoiding Foreclosure', 'Tired Landlords', 'Family Divorce', 'Avoiding Bankruptcies', 'Health or Medical Issues']),
    'Any Condition': ('condition', ['Outdated or Old Houses', 'New Home Builds', 'Damaged by Storms', 'Fire or Water Damage', 'Damage by Termites', 'Full of Trash and/or Stuff', 'Majorly Needs Repairs', 'Tenants Rental Problems', 'Uncompleted Construction']),
    'Any Challenge': ('deadline', ['Financial Problems', 'Title Concerns', 'Violations of Code', 'Hoarder Properties', 'Low Home Equity', 'Large Tax Liens', 'Properties Out of Area', 'Family Issues', 'Mortgage Payments Late']),
}
reasons = ''.join(
    f'<div class="reason reveal"><i>{icon(ic)}</i><h3>{t}</h3><ul class="checks">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul></div>'
    for t, (ic, items) in reason_lists.items())
counties = ''.join(f'<div class="county"><h3>{c}</h3><p>{towns}</p></div>' for c, towns in COUNTIES.items())
if YOUTUBE_ID:
    video = (f'<div class="video-frame"><iframe src="https://www.youtube-nocookie.com/embed/{YOUTUBE_ID}?rel=0" title="Watch how {BRAND} helps Redding homeowners" '
             'loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>')
else:
    video = ('<div class="video-frame video-placeholder"><span class="play" aria-hidden="true"></span>'
             f'<p>{PERSON}’s YouTube video goes here.</p><small>Preview placeholder until the YouTube link is supplied.</small></div>')

home = f'''
<section class="hero" id="top">
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="pill">Redding &amp; Shasta County · Local cash buyer</p>
      <h1>Sell Your Home Fast! <span class="hl">Redding CA</span></h1>
      <p class="lede">#1 Most Trusted Cash Home Buyer in Redding Ca! Get a “no strings attached” cash offer.</p>
      <ul class="hero-points"><li>{icon("check")}Sell as-is</li><li>{icon("check")}Pay no fees</li><li>{icon("check")}On your schedule</li></ul>
      <a class="hero-call" href="{TEL}">{icon("phone")}<span>Prefer to talk? <b>Call {PHONE}</b></span></a>
    </div>
    {lead_form("offer")}
  </div>
</section>

<section class="section reviews" id="stories">
  <div class="container">
    <div class="reviews-head"><div><p class="eyebrow">Google reviews</p><h2>People who were where you are now.</h2></div>{rating_box()}</div>
    <div class="review-grid">{review_cards()}</div>
    <a class="text-link" href="{GOOGLE_URL}" target="_blank" rel="noopener">Read all our reviews on Google {icon("arrow")}</a>
  </div>
</section>

<section class="section video" id="video">
  <div class="container narrow">
    <div class="head center"><p class="eyebrow">See how it works</p><h2>Watch How We Help Redding Homeowners</h2>
      <p>A quick look at how {BRAND} makes selling your house fast, easy, and stress-free.</p></div>
    {video}
  </div>
</section>

<section class="section process" id="process">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">Steps</p><h2>Three simple steps.</h2><p>No fixing up for photos. No weekend showings. Just a conversation about the property and a plan that fits.</p></div>
    <ol class="timeline reveal">
      <li><span class="num">1</span><h3>Connect With Us</h3><p>We help distressed home sellers in Shasta County, CA. Reach out to our team for a smooth cash sale process. We offer fair prices and handle all the details.</p></li>
      <li><span class="num">2</span><h3>Get A Cash Offer</h3><p>We help homeowners sell their properties quickly and with ease, especially those facing distressing situations. Contact us to receive a fair cash offer.</p></li>
      <li><span class="num">3</span><h3>Cash Out On Your Home</h3><p>Sell your house quickly and easily without the hassle of repairs or delays. We provide convenience for distressed home sellers.</p></li>
    </ol>
    <div class="steps-cta">{btn(cls="btn btn-lg")}</div>
  </div>
</section>

<section class="section intro">
  <div class="container intro-grid">
    <div class="intro-copy reveal">
      <p class="eyebrow">Conveniences</p>
      <h2>Get a Free &amp; Fast Cash Offer</h2>
      <p class="big">Sell your house as-is. Pay No Fees. On your schedule. Call <a href="{TEL}">{PHONE}</a>.</p>
      <p><strong>Selling Fast and Easy.</strong> We buy homes quickly in Shasta County, CA, offering fast cash solutions for distressed sellers. Avoid lengthy processes and sell your home with ease.</p>
      <p><strong>No Real Estate Fees or Commissions.</strong> We buy homes directly, so you don’t pay any real estate fees or commissions. This saves you money and time, making the selling process stress-free and simple.</p>
      <p><strong>Sell in As-is Condition with No Repairs.</strong> We buy homes in their current condition. Avoid repair costs and sell your property without extra hassle or delay.</p>
    </div>
    <div class="intro-visual reveal">
      <figure class="photo"><img src="{link("assets/house-blue.jpg")}" alt="A house purchased by {BRAND} in Redding, CA" loading="lazy" decoding="async"></figure>
    </div>
  </div>
</section>

<section class="section compare" id="compare">
  <div class="container">
    <div class="head reveal"><p class="eyebrow">Side by side</p><h2>Traditional Vs {BRAND}</h2><p>See how selling directly to {BRAND} compares with the traditional real estate sale process.</p></div>
    <div class="compare-grid">
      <div class="compare-card cash reveal"><span class="ribbon">{BRAND}</span><h3>Selling to {BRAND}</h3><ul class="checks">
<li><strong>No Fees:</strong><br>Save your money for your next move and close confidently without shelling out any cent with our reliable method.</li>
<li><strong>Highest Price:</strong><br>Maximize your home’s off-market price and get the most out of your property regardless of its condition.</li>
<li><strong>Sell As-is:</strong><br>Forget about sprucing up your property for showings and secure a buyer with us.</li>
<li><strong>Close Quickly:</strong><br>Close confidently in as fast as 10 days or according to your specific schedule.</li>
<li><strong>No Closing Costs:</strong><br>You get cash and don’t have to spend anything once you close.</li>
</ul></div>
      <div class="compare-card trad reveal"><h3>Traditional Real Estate Sale Process</h3><ul class="crosses">
<li><strong>Extra Fees:</strong><br>You may need to shell out certain percentages of the purchase price before you can even close.</li>
<li><strong>Unsure Buyers:</strong><br>People can haggle or change their minds later on, leaving you uncertain and unconfident about whether you’ll close.</li>
<li><strong>Cleaning Up:</strong><br>Selling a property involves making it attractive for potential buyers, which may require you to invest in repairs.</li>
<li><strong>Open Houses:</strong><br>You would need to schedule showings and invite people before you can sell your house.</li>
<li><strong>Long Timeline:</strong><br>Expect to wait at least two months (if you’re lucky) before you can sell your property completely.</li>
</ul></div>
    </div>
  </div>
</section>

<section class="section reasons">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">Any house. Any story.</p><h2>We buy houses for any reason, any condition, any challenge.</h2></div>
    <div class="reason-grid">{reasons}</div>
  </div>
</section>

<section class="section areas-sec" id="areas">
  <div class="container">
    <div class="head reveal"><p class="eyebrow">Where do we buy?</p><h2>We Purchase in Shasta County, Tehama County, Siskiyou County &amp; Butte County!</h2>
      <p>{BRAND} is a family owned and operated real estate investment firm proudly serving Northern California. Our process allows us to deliver offers quickly, often within 7-14 days, whatever the condition of the home.</p></div>
    <div class="county-grid reveal">{counties}</div>
  </div>
</section>

<section class="section riz" id="oscar">
  <div class="container riz-grid">
    <div class="riz-visual reveal">
      <figure class="photo"><img src="{link("assets/house-fence.jpg")}" alt="A Redding home purchased by {BRAND}" width="1300" height="975" loading="lazy"></figure></div>
    <div class="riz-copy reveal">
      <p class="eyebrow">Meet your local buyer</p>
      <h2>It starts with a conversation with {PERSON}.</h2>
      <p class="kicker">{BRAND} is a family owned and operated real estate investment firm proudly serving Northern California.</p>
      <p>We specialize in providing cash offers for homes in Northern California and pride ourselves on our relationships with local homeowners as well as the Realtor community. We understand that every customer is unique, so we strive to always be fair and honest with our clients.</p>
      <a class="text-link" href="{link("about/")}">Get to know {BRAND} {icon("arrow")}</a>
    </div>
  </div>
</section>

<section class="section faqs" id="faq">
  <div class="container faq-grid">
    <div class="head reveal"><p class="eyebrow">Good questions. Straight answers.</p><h2>Before you take the next step.</h2><a class="text-link" href="{link("faq/")}">All frequently asked questions {icon("arrow")}</a></div>
    <div class="faq-list reveal">
      <details><summary>Do I need to repair or clean out the house?</summary><p>No. We buy homes in their current condition, from tenant issues to fire damage and beyond. Tell us about the condition and anything you’d prefer to leave behind.</p></details>
      <details><summary>Is there any obligation to accept an offer?</summary><p>No. There is absolutely no pressure to accept the offer; you can take the time to review your options without any commitment.</p></details>
      <details><summary>How quickly could we close?</summary><p>In as fast as 10 days, or according to your specific schedule, where the property and title allow. Offers often come within 7-14 days.</p></details>
      <details><summary>How do I get paid?</summary><p>If the offer works for you, you accept it and we open Escrow. Once Escrow closes, the proceeds get wired directly into your bank account.</p></details>
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
print(f'Built {len(written)} pages ({len(posts)} blog articles) and the homepage.')
