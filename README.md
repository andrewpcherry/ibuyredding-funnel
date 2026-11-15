# IBuyRedding — replacement website preview

Built from the REI template default (andrewpcherry/homebuyerswi-funnel), rebranded for IBuyRedding (ibuyredding.com), a brand of Manzo Capital LLC. The current production site and DNS are unchanged.

- v2 design across every page with IBuyRedding branding: sky blue `#24B2E3`, black, accent yellow `#FFCC00`, Bree Serif headings, IBuyRedding logo and favicon, Oscar Manzo's photo and the client's own property photos.
- Every ibuyredding.com page path is kept: home, about, FAQ, inherited house, local businesses, privacy policy, the blog index and all 145 blog posts. Source snapshot: 16 November 2026.
- Google rating badge: 5.0 stars, 12 reviews, with the three verbatim 5-star reviews shown on ibuyredding.com.
- Multi-situation assessment at `get-a-cash-offer-today/`, rebranded for Redding: service area (Shasta, Tehama, Siskiyou and Butte counties), phone (530) 638-2296, Redding price bands.
- Preview pages are noindex. Contact fields are demonstration-only, make no network request and emit no conversion events.

## Before launch

- Confirm IBuyRedding's own SMS consent wording. The assessment still uses the template's wording.
- Connect inquiry delivery to the client's CRM and test a conversion.
- Swap the preview base path (`/ibuyredding-funnel/`) and noindex settings, then get client approval before any DNS change.

## Files

`site-source/build.py` generates the site from the snapshot (kept outside this repo; set `IBR_SNAPSHOT` to its folder). `assets/site.css` and `assets/site.js` supply shared presentation and interactions. `migration/url-map.csv` and `migration/sitemap-production.xml` list the production URLs.
