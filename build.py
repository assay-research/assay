#!/usr/bin/env python3
"""Assemble the standalone site files from the partials in src/.

Why a build step at all: the same two pages are published in two places. As a
Claude artifact the host supplies the <!doctype>, <head> and a small CSS reset,
so src/*.html are written as partials with no document wrapper. A web server
supplies nothing, so this script adds the wrapper, the reset, and the metadata,
and rewrites the cross-links between the two pages for whichever target.

    python3 build.py            # write index.html and check/index.html
    python3 build.py --artifact # print the artifact-shaped partials instead

No dependencies, stdlib only, Python 3.6+. Run it after editing anything in
src/ and commit both the source and the generated file.
"""
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Where each partial lands on the site, and the two pieces of metadata a real
# web page needs that an artifact does not: a description for search results
# and link previews, and the relative path each page uses to reach the other.
PAGES = [
    {
        "src": "src/article.html",
        "out": "index.html",
        "icon": "favicon.svg",
        "description": (
            "Six checkable defects in Hyperliquid copy-trading leaderboards, "
            "measured across all 47,190 ranked accounts. Two in five excluded "
            "accounts were dead ones still being ranked, and a $200 account can "
            "follow 32 of the 143 traders that survive every test."
        ),
        # from the site root, the tool lives one directory down
        "links": {"TOOL": "check/", "ARTICLE": "./"},
    },
    {
        "src": "src/tool.html",
        "out": "check/index.html",
        "icon": "../favicon.svg",
        "description": (
            "Paste a Hyperliquid address and read the checks a return ranking "
            "leaves out: whether it still trades, how many losses its edge is "
            "estimated from, and how much of its order flow your account could "
            "actually place. Runs in your browser, nothing stored."
        ),
        # from check/, the article is the parent directory
        "links": {"TOOL": "./", "ARTICLE": "../"},
    },
]

# The artifact host injects this much for free. A web server does not, so the
# site build has to carry it or the pages lose their safe-area padding, their
# box-sizing and the native behaviour of the hidden attribute.
RESET = """\
<style>
/* Supplied by the artifact host; written out explicitly for the standalone site. */
:root{
  color-scheme:light;
  padding-top:env(safe-area-inset-top,0px);
  padding-bottom:env(safe-area-inset-bottom,0px);
}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*{box-sizing:border-box}
img{max-width:100%}
[hidden]:not([hidden="until-found"]){display:none!important}
</style>"""

DOC = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{title}
<meta name="description" content="{description}">
<meta name="robots" content="index,follow">
<link rel="icon" href="{icon}" type="image/svg+xml">
<meta property="og:type" content="article">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<!-- Add og:url and <link rel="canonical"> once the public URL is known.
     Both need the full absolute address, so they cannot be filled in before
     the GitHub Pages URL exists. See README.md. -->
{links}
{reset}
{style}
</head>
<body>
{body}
</body>
</html>
"""


def split_partial(text, src):
    """Pull the <title>, the <link> tags, the <style> block and the body apart."""
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    if not m:
        sys.exit("%s: no <title> found" % src)
    title_tag, title_text = m.group(0), m.group(1).strip()

    links = re.findall(r'<link\b[^>]*>', text)

    styles = re.findall(r"<style>.*?</style>", text, re.S)
    if len(styles) != 1:
        sys.exit("%s: expected exactly one <style> block, found %d" % (src, len(styles)))
    style = styles[0]

    body = text
    for chunk in [title_tag] + links + [style]:
        body = body.replace(chunk, "", 1)
    return title_tag, title_text, links, style, body.strip()


def escape(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def resolve(text, links):
    """Replace the {{TOOL}} / {{ARTICLE}} tokens, and refuse to ship a stray one."""
    for key, value in links.items():
        text = text.replace("{{%s}}" % key, value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if leftover:
        sys.exit("unresolved link token(s): %s" % ", ".join(sorted(set(leftover))))
    return text


def build_site():
    for page in PAGES:
        src = os.path.join(HERE, page["src"])
        text = io.open(src, encoding="utf-8").read()
        title_tag, title_text, links, style, body = split_partial(text, page["src"])

        html = DOC.format(
            title=title_tag,
            description=escape(page["description"]),
            og_title=escape(title_text),
            links="\n".join(links),
            icon=page["icon"],
            reset=RESET,
            style=style,
            body=resolve(body, page["links"]),
        )

        out = os.path.join(HERE, page["out"])
        out_dir = os.path.dirname(out)
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        io.open(out, "w", encoding="utf-8").write(html)
        print("wrote %-18s %6d bytes  (%s)" % (page["out"], len(html.encode("utf-8")),
                                               title_text))


# The artifact host wants the partial with no document wrapper, and the
# cross-links pointing at the published artifact URLs rather than at paths.
ARTIFACT_LINKS = {
    "ARTICLE": "https://claude.ai/artifact/RqF4YQhE3mByRQbE3EaYZH",
    "TOOL": "https://claude.ai/artifact/Pg5asunWLeZPwPpvmabavs",
}


def build_artifacts():
    out_dir = os.path.join(HERE, "build", "artifact")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    for page in PAGES:
        text = io.open(os.path.join(HERE, page["src"]), encoding="utf-8").read()
        name = os.path.basename(page["src"])
        out = os.path.join(out_dir, name)
        io.open(out, "w", encoding="utf-8").write(resolve(text, ARTIFACT_LINKS))
        print("wrote build/artifact/%-14s %6d bytes" % (name, os.path.getsize(out)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artifact", action="store_true",
                    help="write the artifact-shaped partials to build/artifact/ instead")
    args = ap.parse_args()
    build_artifacts() if args.artifact else build_site()
