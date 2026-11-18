# IBuyRedding — replacement website preview

Built from the REI template default (andrewpcherry/homebuyerswi-funnel), rebranded for IBuyRedding (ibuyredding.com), a brand of Manzo Capital LLC. Custom-domain deployment is configured for ibuyredding.com. Intake remains in preview mode pending delivery implementation and acceptance.

- Simplified to match cash.ibuyredding.com (client feedback, 17 November 2026): one primary blue (the logo blue `#38B6FF`) for every button, link and highlight; white and light gray sections; navy text; dark photo hero. Official IBuyRedding logo, roof-icon favicon, Bree Serif headings.
- Link preview: `img/og-image.png` (logo on black, 1200x630) on every page; homepage title "IBuyRedding | Sell Your House Fast for Cash in Redding, CA".
- Header is logo, phone button and menu only. No review ticker.
- Every ibuyredding.com page path is kept: home, about, FAQ, inherited house, local businesses, privacy policy, the blog index and all 145 blog posts. Source snapshot: 16 November 2026.
- Google rating badge: 5.0 stars, 12 reviews, with the three verbatim 5-star reviews shown on ibuyredding.com.
- Contact-first lead form in the homepage hero and at `get-a-cash-offer-today/`: step 1 First Name, Last Name, Property Address, Phone, optional SMS consent, Email (optional); step 2 optional situation questions. Reviews and a video section sit directly below the hero form.
- The homepage video shows a placeholder until Oscar sends the YouTube link (set `YOUTUBE_ID` in `site-source/build.py`).
- The multi-situation assessment is no longer built (the form now starts with contact details); its source stays in `site-source/`.
- Preview pages are noindex. The home and cash-offer pages embed the native HighLevel inquiry survey. The static site emits no conversion events.

## Before launch

- SMS consent uses the client's wording (16 November 2026): optional, unchecked, not required to submit, inquiry and appointment messages only. Promotional texting would need separate consent. `sms-terms/` covers the program; SMS Terms and Privacy Policy are linked beside the checkbox and in the footer.
- The Privacy Policy was rewritten around what this site does and now protects mobile numbers and SMS consent records from third-party marketing. Manzo should confirm it matches its actual practices (CRM and messaging providers, analytics and ad tags, data requests) before launch.
- The site says "Call" only until texting on the public number (530) 638-2296 is verified. Never publish Oscar's private notification number.
- Keep preview mode until inquiry delivery is finished: step 1 should post the lead to GHL (so drop-offs are captured) and step 2 should update it. Test receipt in Manzo's GHL account, Oscar's notification and conversion tracking before showing a genuine success message.
- Asset/navigation paths and OG_IMAGE now use ibuyredding.com.
- Production paths are configured; retain noindex until live intake and conversion acceptance. DNS changes were performed by Oscar; Andrew authorized the custom-domain binding on 17 November 2026.

## Files

`site-source/build.py` generates the site from the snapshot (kept outside this repo; set `IBR_SNAPSHOT` to its folder). `assets/site.css` and `assets/site.js` supply shared presentation and interactions. `migration/url-map.csv` and `migration/sitemap-production.xml` list the production URLs.
