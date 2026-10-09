# Apps site

Privacy policies, terms and support pages for four iOS apps (Prunely, Quitline, Lumenwise, Paperlark), served by GitHub Pages at
https://biglerclaw-lgtm.github.io/apps-site/

## Editing

- Page sources live in `src/` (shared bits in `src/_partials/`, page shell in `src/_layout.html`).
- App names, the support email and dates live in `site.json`.
- Rebuild after any change: `python build.py` (no dependencies), then commit the generated `.html` files.

## Before submission

`SUPPORT_EMAIL` in `site.json` is the placeholder `SUPPORT_EMAIL_TBD`. Set the real address, rebuild, commit and push.

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

Lumenwise and Paperlark policies and terms are effective 2026-10-09; they override `EFFECTIVE_DATE` in their page front matter.

When a policy changes: update the text, add a changelog row, bump `EFFECTIVE_DATE` in `site.json` if needed, and keep the
App Store privacy label in sync.
