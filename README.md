# IBuyRedding — replacement website preview

Built from the REI template default (andrewpcherry/homebuyerswi-funnel), rebranded for IBuyRedding (ibuyredding.com), a brand of Manzo Capital LLC. The current production site and DNS are unchanged.

- v2 design across every page with IBuyRedding branding: sky blue `#24B2E3`, black, accent yellow `#FFCC00`, Bree Serif headings, IBuyRedding logo and favicon, Oscar Manzo's photo and the client's own property photos.
- Every ibuyredding.com page path is kept: home, about, FAQ, inherited house, local businesses, privacy policy, the blog index and all 145 blog posts. Source snapshot: 16 November 2026.
- Google rating badge: 5.0 stars, 12 reviews, with the three verbatim 5-star reviews shown on ibuyredding.com.
- Multi-situation assessment at `get-a-cash-offer-today/`, rebranded for Redding: service area (Shasta, Tehama, Siskiyou and Butte counties), phone (530) 638-2296, Redding price bands.
- Preview pages are noindex. Contact fields are demonstration-only, make no network request and emit no conversion events.

## Before launch

- SMS consent uses the client's wording (16 November 2026): optional, unchecked, not required to submit, inquiry and appointment messages only. Promotional texting would need separate consent. `sms-terms/` covers the program; SMS Terms and Privacy Policy are linked beside the checkbox and in the footer.
- The Privacy Policy was rewritten around what this site does and now protects mobile numbers and SMS consent records from third-party marketing. Manzo should confirm it matches its actual practices (CRM and messaging providers, analytics and ad tags, data requests) before launch.
- The site says "Call" only until texting on the public number (530) 638-2296 is verified. Never publish Oscar's private notification number.
- Keep preview mode until inquiry delivery is finished: test receipt in Manzo's GHL account, Oscar's notification and conversion tracking before showing a genuine success message.
- Swap the preview base path (`/ibuyredding-funnel/`) and noindex settings, then get client approval before any DNS change.

## Files

`site-source/build.py` generates the site from the snapshot (kept outside this repo; set `IBR_SNAPSHOT` to its folder). `assets/site.css` and `assets/site.js` supply shared presentation and interactions. `migration/url-map.csv` and `migration/sitemap-production.xml` list the production URLs.
