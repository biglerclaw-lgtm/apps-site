#!/usr/bin/env python3
"""Build the static site.

Edit pages in src/ and app names/dates/support email in site.json, then run:  python build.py
Generated .html files are written next to this script (the GitHub Pages root).

Template syntax (no dependencies):
  {{KEY}}         value from site.json or the page's front matter (unknown keys fail the build)
  {{APP}}         the page's app name (front matter `app: swipeclean` -> site.json SWIPECLEAN_NAME)
  {{> name}}      include src/_partials/name.html (partials may use {{...}} too)
  {{root}}        relative path back to the site root ("" or "../")

Front matter is an HTML comment at the very top of a src page:
  <!--
  title: Privacy Policy
  description: One sentence for search results.
  app: swipeclean            (optional)
  -->
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
}

FRONT = re.compile(r"\A\s*<!--(.*?)-->\s*", re.S)
PARTIAL = re.compile(r"\{\{>\s*([\w-]+)\s*\}\}")
VAR = re.compile(r"\{\{\s*([A-Za-z_][\w]*)\s*\}\}")


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
    root = env["root"]
    if app:
        base = ""  # app pages live in the app folder
        items = [
            ("index.html", "Overview"),
            ("privacy.html", "Privacy"),
            ("terms.html", "Terms"),
            ("support.html", "Support"),
        ]
    else:
        base = ""
        items = [
            ("index.html", "Apps"),
            ("privacy.html", "Privacy"),
            ("terms.html", "Terms"),
        ]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if href == page else ""
        out.append(f'<li><a href="{base}{href}"{cur}>{label}</a></li>')
    return "\n          ".join(out)


def main():
    site = json.loads((HERE / "site.json").read_text(encoding="utf-8"))
    layout = (SRC / "_layout.html").read_text(encoding="utf-8")
    pages = [p for p in SRC.rglob("*.html") if not p.name.startswith("_") and "_partials" not in p.parts]
    for path in sorted(pages):
        rel = path.relative_to(SRC)
        meta, body = parse(path)
        depth = len(rel.parts) - 1
        env = dict(site)
        env["root"] = "../" * depth
        app = meta.get("app", "")
        env["APP"] = site[APPS[app]["name_key"]] if app else "Apps"
        env["APP_SLUG"] = app
        env["APP_Q"] = quote(env["APP"])  # URL-encoded name for mailto subjects
        env["APP_URL"] = site["SITE_URL"] + (f"{app}/" if app else "")
        env.update({k: v for k, v in meta.items() if k not in ("app",)})
        env["title"] = fill(meta.get("title", ""), env, rel)
        env["description"] = fill(meta.get("description", ""), env, rel)
        env["NAV"] = nav_html(app, rel, env)
        env["SECTION"] = env["APP"]
        env["SECTION_HREF"] = "index.html"
        env["BODY"] = fill(expand_partials(body), env, rel)
        html = fill(expand_partials(layout), env, rel)
        out = HERE / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8", newline="\n")
        print(f"built {rel.as_posix()}")


if __name__ == "__main__":
    main()
