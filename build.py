#!/usr/bin/env python3
"""Build the static site.

Edit pages in src/ and app names/dates/support email in site.json, then run:  python build.py
Generated .html files are written next to this script (the GitHub Pages root).

Set the support address (the only place it lives is site.json), then rebuild:
  python build.py --support-email help@example.com
  python build.py

Template syntax (no dependencies):
  {{KEY}}         value from site.json or the page's front matter (unknown keys fail the build)
  {{APP}}         the page's app name (front matter `app: swipeclean` -> site.json SWIPECLEAN_NAME)
  {{> name}}      include src/_partials/name.html (partials may use {{...}} too)
  {{root}}        relative path back to the site root ("" or "../")
  {{#ads}}...{{/ads}}   kept only when the page's app has "ads": true in site.json "apps"
  {{^ads}}...{{/ads}}   kept only when it is false (the ad-free version)
                  A tag alone on its line takes the line with it. Blocks for different keys may nest;
                  blocks for the same key may not. Front matter values may use them on one line.

Front matter is an HTML comment at the very top of a src page:
  <!--
  title: Privacy Policy
  description: One sentence for search results.
  app: swipeclean            (optional)
  -->

Every app's privacy, terms and support page is also written to <app>/<page>/index.html, so
.../quitline/privacy, .../quitline/privacy/ and .../quitline/privacy.html all open the same page.
"""
import json
from urllib.parse import quote
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
PARTIALS = SRC / "_partials"

APPS = {
    "swipeclean": {"name_key": "SWIPECLEAN_NAME"},
    "quitline": {"name_key": "QUITLINE_NAME"},
    "lumenwise": {"name_key": "LUMENWISE_NAME"},
    "paperlark": {"name_key": "PAPERLARK_NAME"},
    "fastbloom": {"name_key": "FASTBLOOM_NAME"},
}

# App pages that also get an extensionless copy at <app>/<page>/index.html (App Store Connect URLs).
ALIASED_PAGES = ("privacy", "terms", "support")

# Words that must never appear on a page of an app whose "ads" switch is false. The ad-free wording
# avoids all of them, so a match means an ads-only sentence escaped its {{#ads}} block.
AD_ONLY_TERMS = [
    "AppLovin", "AdMob", "IDFA", "IDFV", "Tracking Transparency", "Ad Privacy Choices",
    "Do not sell", "removes ads", "removes all ads", "remove ads", "and no ads", "rewarded",
    "ad SDK", "ad partner", "ad network", "interstitial", "banner", "consent screen",
    "consent manager", "consent form", "personalized ads", "My Ad Center", "shows ads",
    "funded by ads", "switch off ads", "ads in the free version", "free version shows",
]

FRONT = re.compile(r"\A\s*<!--(.*?)-->\s*", re.S)
PARTIAL = re.compile(r"\{\{>\s*([\w-]+)\s*\}\}")
VAR = re.compile(r"\{\{\s*([A-Za-z_][\w]*)\s*\}\}")
COND = re.compile(r"\{\{([#^])(\w+)\}\}(.*?)\{\{/\2\}\}", re.S)
COND_LINE = re.compile(r"(?m)^[ \t]*(\{\{[#^/]\w+\}\})[ \t]*\n")
COND_LEFT = re.compile(r"\{\{[#^/]\w+\}\}")
RELATIVE_URL = re.compile(r"""(\b(?:href|src)=")(?![a-zA-Z][a-zA-Z0-9+.-]*:|#|/|\?)""")
EMAIL_KEY = re.compile(r'("SUPPORT_EMAIL"\s*:\s*")[^"]*(")')


def parse(path):
    text = path.read_text(encoding="utf-8")
    meta = {}
    m = FRONT.match(text)
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def expand_partials(text, depth=0):
    if depth > 5:
        sys.exit("partial nesting too deep")

    def sub(m):
        p = PARTIALS / f"{m.group(1)}.html"
        if not p.exists():
            sys.exit(f"missing partial: {p}")
        return expand_partials(p.read_text(encoding="utf-8"), depth + 1)

    return PARTIAL.sub(sub, text)


def conditionals(text, flags, where):
    """Resolve {{#key}}...{{/key}} (kept when flags[key] is true) and {{^key}}...{{/key}} (when false)."""
    text = COND_LINE.sub(r"\1", text)

    def sub(m):
        kind, key, inner = m.groups()
        if key not in flags:
            sys.exit(f"{where}: unknown switch {{{{{kind}{key}}}}}")
        keep = flags[key] if kind == "#" else not flags[key]
        return inner if keep else ""

    prev = None
    while prev != text:
        prev, text = text, COND.sub(sub, text)
    left = COND_LEFT.search(text)
    if left:
        sys.exit(f"{where}: unbalanced {left.group(0)}")
    return text


def fill(text, env, where):
    def sub(m):
        k = m.group(1)
        if k not in env:
            sys.exit(f"{where}: unknown placeholder {{{{{k}}}}}")
        return env[k]

    # two passes so values may contain placeholders (e.g. {{APP}} inside a site.json value)
    return VAR.sub(sub, VAR.sub(sub, text))


def nav_html(app, rel, env):
    page = rel.name
    if app:
        items = [
            ("index.html", "Overview"),
            ("privacy.html", "Privacy"),
            ("terms.html", "Terms"),
            ("support.html", "Support"),
        ]
    else:
        items = [
            ("index.html", "Apps"),
            ("privacy.html", "Privacy"),
            ("terms.html", "Terms"),
        ]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if href == page else ""
        out.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "\n          ".join(out)


def support_links(env, app):
    """Contact markup. While SUPPORT_EMAIL is a placeholder (no "@"), it is shown as plain text and
    buttons point at the support page: never a mailto: link to a non-address (App Review 1.5).

      {{SUPPORT_LINK}}       the address, linked with mailto: once it is real
      {{SUPPORT_LINK_SUBJ}}  same, with "<App> support" as the mail subject
      {{SUPPORT_HREF}}       href for a contact button: mailto (real) or the support page (placeholder)
    """
    email = env["SUPPORT_EMAIL"]
    if "@" in email:
        env["SUPPORT_LINK"] = f'<a href="mailto:{email}">{email}</a>'
        env["SUPPORT_LINK_SUBJ"] = f'<a href="mailto:{email}?subject={env["APP_Q"]}%20support">{email}</a>'
        env["SUPPORT_HREF"] = f'mailto:{email}?subject={env["APP_Q"]}%20support'
    else:
        env["SUPPORT_LINK"] = env["SUPPORT_LINK_SUBJ"] = f'<span class="email">{email}</span>'
        env["SUPPORT_HREF"] = "support.html#contact" if app else "#contact"


def load_apps(site):
    """site.json "apps": per-app switches and dates, e.g. {"quitline": {"ads": false, "LAST_UPDATED": "..."}}."""
    cfg = site.pop("apps", None)
    if not isinstance(cfg, dict) or set(cfg) != set(APPS):
        sys.exit(f'site.json: "apps" must have exactly these keys: {", ".join(APPS)}')
    for slug, c in cfg.items():
        if not isinstance(c.get("ads"), bool):
            sys.exit(f"site.json: apps.{slug}.ads must be true or false")
        if not isinstance(c.get("LAST_UPDATED"), str) or not c["LAST_UPDATED"]:
            sys.exit(f"site.json: apps.{slug}.LAST_UPDATED is missing")
    return cfg


def set_support_email(address):
    """Write a new SUPPORT_EMAIL into site.json, keeping the rest of the file byte for byte."""
    address = address.strip()
    if not re.fullmatch(r"[^@\s\"<>]+@[^@\s\"<>]+\.[^@\s\"<>]+", address):
        sys.exit(f"not an email address: {address!r}")
    path = HERE / "site.json"
    text = path.read_text(encoding="utf-8")
    new, n = EMAIL_KEY.subn(lambda m: m.group(1) + address + m.group(2), text)
    if n != 1:
        sys.exit('site.json: expected exactly one "SUPPORT_EMAIL" entry')
    path.write_text(new, encoding="utf-8", newline="\n")
    print(f"SUPPORT_EMAIL is now {address}. Next: python build.py")


def check_ad_free(html, where):
    low = html.lower()
    for term in AD_ONLY_TERMS:
        if term.lower() in low:
            sys.exit(f'{where}: ad-free page contains "{term}" (wrap that text in {{{{#ads}}}}...{{{{/ads}}}})')


def write(out, html):
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")


def main():
    args = sys.argv[1:]
    if args:
        if len(args) == 2 and args[0] == "--support-email":
            return set_support_email(args[1])
        sys.exit("usage: python build.py [--support-email ADDRESS]")

    site = json.loads((HERE / "site.json").read_text(encoding="utf-8"))
    apps_cfg = load_apps(site)
    layout = (SRC / "_layout.html").read_text(encoding="utf-8")
    pages = [p for p in SRC.rglob("*.html") if not p.name.startswith("_") and "_partials" not in p.parts]
    written = []
    for path in sorted(pages):
        rel = path.relative_to(SRC)
        meta, body = parse(path)
        depth = len(rel.parts) - 1
        env = dict(site)
        env["root"] = "../" * depth
        app = meta.get("app", "")
        if app:
            flags = {"ads": apps_cfg[app]["ads"]}
            env["LAST_UPDATED"] = apps_cfg[app]["LAST_UPDATED"]
        else:
            flags = {"ads": any(c["ads"] for c in apps_cfg.values())}
        env["APP"] = site[APPS[app]["name_key"]] if app else "Apps"
        env["APP_SLUG"] = app
        env["APP_Q"] = quote(env["APP"])  # URL-encoded name for mailto subjects
        env["APP_URL"] = site["SITE_URL"] + (f"{app}/" if app else "")
        env["CANONICAL"] = site["SITE_URL"] + rel.as_posix()
        support_links(env, app)
        meta = {k: conditionals(v, flags, rel) for k, v in meta.items()}
        env.update({k: v for k, v in meta.items() if k not in ("app",)})
        env["title"] = fill(meta.get("title", ""), env, rel)
        env["description"] = fill(meta.get("description", ""), env, rel)
        env["NAV"] = nav_html(app, rel, env)
        env["SECTION"] = env["APP"]
        env["SECTION_HREF"] = "index.html"
        env["BODY"] = fill(conditionals(expand_partials(body), flags, rel), env, rel)
        html = fill(conditionals(expand_partials(layout), flags, rel), env, rel)
        if app and not flags["ads"]:
            check_ad_free(html, rel)
        write(HERE / rel, html)
        written.append((rel.as_posix(), html))
        print(f"built {rel.as_posix()}")
        if app and rel.stem in ALIASED_PAGES:
            # Same page one folder deeper: every relative link and asset gets one more "../".
            alias = rel.parent / rel.stem / "index.html"
            alias_html = RELATIVE_URL.sub(r"\1../", html)
            write(HERE / alias, alias_html)
            written.append((alias.as_posix(), alias_html))
            print(f"built {alias.as_posix()} (same page as {rel.as_posix()})")

    email = site["SUPPORT_EMAIL"]
    missing = [name for name, html in written if email not in html]
    if missing:
        sys.exit(f"SUPPORT_EMAIL {email!r} missing from: {', '.join(missing)}")
    print(f"SUPPORT_EMAIL {email!r} is on all {len(written)} pages")


if __name__ == "__main__":
    main()
