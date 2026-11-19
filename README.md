# Apps site

Privacy policies, terms and support pages for five iOS apps (Prunely, Quitline, Lumenwise, Paperlark, Fastbloom), served by GitHub Pages at
https://biglerclaw-lgtm.github.io/apps-site/

## Editing

- Page sources live in `src/` (shared bits in `src/_partials/`, page shell in `src/_layout.html`).
- App names, the support email and dates live in `site.json`.
- Rebuild after any change: `python build.py` (no dependencies), then commit the generated `.html` files.
- Per-app switches live in `site.json` under `"apps"`: `"ads"` (true or false) and `"LAST_UPDATED"` (the
  "Last updated" date on that app's privacy policy and terms; in the ad-free pages it is also the
  "Effective" date of the 1.0 version). Each app also sets the wording the shared partials need:
  `"PRO_SUMMARY"` (what Pro adds), `"FAMILY_SHARING"` (which purchases are family-shareable),
  `"SETTINGS_PATH"` (how to reach the app's Settings) and `"REFUND_IN_APP"` (the in-app "Request a
  refund" sentence, or "" if the app has none); the build fails if one is missing (`APP_KEYS` in
  `build.py`). Template text that only applies to a
  version with ads sits in `{{#ads}}...{{/ads}}`, the ad-free wording in `{{^ads}}...{{/ads}}`.
  With `"ads": false` the build fails if an ad-only phrase (AppLovin, AdMob, IDFA, "Do not sell or share", "removes ads",
  "rewarded" and more; the list is `AD_ONLY_TERMS` in `build.py`) is left on any page of that app.
- Every app's privacy, terms and support page is also written to `<app>/<page>/index.html` (same content,
  relative links adjusted, canonical link to the `.html` page), so `.../quitline/privacy`,
  `.../quitline/privacy/` and `.../quitline/privacy.html` all open it. Never edit those copies by hand.

- All five apps are `"ads": false` for version 1.0 (no ad SDK, no tracking, no tracking prompt, no ad consent). To publish
  pages for a version with ads, set that app's `"ads"` to `true`, bump its `"LAST_UPDATED"`, rebuild, and add a changelog row.
- `APP_DATA_WHERE` and `APP_DATA_TRANSFERS` (defaults in `site.json`) describe where app data lives in the ad-free
  "Your privacy rights" section; Fastbloom overrides both in its privacy front matter because of its iCloud copy of fasts.

## Before submission: the support email

`SUPPORT_EMAIL` in `site.json` is the placeholder `SUPPORT_EMAIL_TBD`, and it is the only place the address lives.
To set the real address on every page, run these two commands in this folder, then commit and push:

```
python build.py --support-email you@example.com
python build.py
```

The first command replaces only the `SUPPORT_EMAIL` value in `site.json` (you can also edit that one line by hand).
The second regenerates all 38 pages and fails if any page does not contain the address.
While it has no `@`, `build.py` renders it as plain text and contact buttons link to the app's `support.html#contact`;
never a `mailto:` link (App Review 1.5). Pages use `{{SUPPORT_LINK}}`, `{{SUPPORT_LINK_SUBJ}}` and `{{SUPPORT_HREF}}`, which become
real `mailto:` links once the address is set.

The ads partial's consent-manager item is `ADS_CONSENT_ITEM` (default in `site.json`; Lumenwise, Paperlark and Fastbloom override it in
their privacy page front matter because their consent form covers only the EEA, UK and Switzerland).

## Renaming an app (e.g. SwipeClean -> Prunely, done 2026-10-08)

Change `SWIPECLEAN_NAME` in `site.json`, run `python build.py`, commit and push. Every page uses that one value.
The URL path `/swipeclean/` stays the same so links already in the app keep working.

## URLs for App Store Connect

| App | Privacy Policy URL | Support URL | Terms (EULA) |
|---|---|---|---|
| Prunely (path /swipeclean/) | https://biglerclaw-lgtm.github.io/apps-site/swipeclean/privacy.html | https://biglerclaw-lgtm.github.io/apps-site/swipeclean/support.html | https://biglerclaw-lgtm.github.io/apps-site/swipeclean/terms.html |
| Quitline | https://biglerclaw-lgtm.github.io/apps-site/quitline/privacy.html | https://biglerclaw-lgtm.github.io/apps-site/quitline/support.html | https://biglerclaw-lgtm.github.io/apps-site/quitline/terms.html |
| Lumenwise | https://biglerclaw-lgtm.github.io/apps-site/lumenwise/privacy.html | https://biglerclaw-lgtm.github.io/apps-site/lumenwise/support.html | https://biglerclaw-lgtm.github.io/apps-site/lumenwise/terms.html |
| Paperlark | https://biglerclaw-lgtm.github.io/apps-site/paperlark/privacy.html | https://biglerclaw-lgtm.github.io/apps-site/paperlark/support.html | https://biglerclaw-lgtm.github.io/apps-site/paperlark/terms.html |
| Fastbloom | https://biglerclaw-lgtm.github.io/apps-site/fastbloom/privacy.html | https://biglerclaw-lgtm.github.io/apps-site/fastbloom/support.html | https://biglerclaw-lgtm.github.io/apps-site/fastbloom/terms.html |

Lumenwise and Paperlark policies and terms are effective 2026-10-09, Fastbloom's 2026-10-13; they override `EFFECTIVE_DATE` in their page front matter.

When a policy changes: update the text, add a changelog row, bump `EFFECTIVE_DATE` in `site.json` if needed, and keep the
App Store privacy label in sync.
