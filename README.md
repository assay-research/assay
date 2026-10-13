# Leaderboard Reality Check

Two static pages about copy-trading leaderboards on Hyperliquid.

| page | path | what it is |
|---|---|---|
| **What the Leaderboards Hide** | `/` | The measurement. All 47,190 ranked accounts screened, every exclusion counted, six defects written up as six findings, with the method and its limits stated. |
| **Leaderboard Reality Check** | `/check/` | The tool. Paste one Hyperliquid address, get nine pass/warn/fail checks and a copyability table for $100 / $200 / $400 / $1,000 accounts. |

## There is no backend, and there does not need to be one

Hyperliquid's info API answers browser requests directly — it returns
`access-control-allow-origin: *` — so the tool calls
`POST https://api.hyperliquid.xyz/info` from the visitor's own browser. Nothing is
proxied, nothing is stored, no API key exists, and no visitor data ever reaches us.

That makes this a folder of static files. Any plain web host serves it, including
GitHub Pages, at no cost.

## Layout

```
src/article.html      the article, as a partial
src/tool.html         the tool, as a partial
build.py              wraps the partials into standalone pages
index.html            GENERATED from src/article.html -- do not edit by hand
check/index.html      GENERATED from src/tool.html   -- do not edit by hand
404.html              hand-written, not generated
robots.txt
```

### Why the partials exist

The same two pages are published twice: here, and as Claude artifacts used for
previewing. The artifact host injects the `<!doctype>`, the `<head>` and a small
CSS reset; a web server injects nothing. So the pages are written as partials
without a document wrapper, and `build.py` adds the wrapper, the reset and the
page metadata for whichever target.

It also rewrites the links between the two pages. In the partials they are the
tokens `{{ARTICLE}}` and `{{TOOL}}`; the site build turns them into relative
paths, the artifact build into `claude.ai` URLs. The build refuses to write a
file with an unresolved token left in it.

### Editing

Edit `src/`, then rebuild and commit both:

```sh
python3 build.py              # regenerates index.html and check/index.html
python3 build.py --artifact   # writes build/artifact/*.html for re-publishing
```

Stdlib Python 3 only, no dependencies, no node, no bundler.

### Preview locally

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. Use the server rather than opening the file
directly — relative links and `/check/` only resolve properly over HTTP.

## Before the first publish

Two things in `build.py` need the real public URL and cannot be filled in until it
exists. Both are marked with comments in the generated HTML:

1. `<meta property="og:url">` and `<link rel="canonical">` in the `DOC` template.
2. The `Sitemap:` line in `robots.txt`.

Neither breaks anything by being absent. Link previews just carry no URL.

## What does not go in this repo

Decided deliberately, not left for later:

- **No ad slots and no ad script.** A tool is read once per visit, which is the
  worst possible shape for display advertising, and crypto is a permission-gated
  category in Google's ad system, so the advertisers who would want this reader
  largely cannot bid. Adding rails now would make the site look like the thing it
  exists to check.
- **No exchange affiliate or referral links, at any price.** A site whose answer is
  usually "don't copy this one" cannot be funded by referrals to the venues where
  you would.
- **No ranking, no suggested position size, and no order placement.** Telling
  someone who to copy and at what size is a personal recommendation on a financial
  instrument, and executing it for them is managing their money. Both are regulated
  activities in the EU. This stays a measurement of public data.
- **No secrets.** Nothing here reads a key or a credential, and `.gitignore` covers
  `.env` and `*.session` so nothing of that kind can be committed by accident.

## Figures

Every number on the article page is reproducible from a one-off sweep of the
Hyperliquid leaderboard and the cached fills of roughly a thousand addresses. The
headline copyability figures — 7 traders followable at $99, 32 at $200, 50 at $400 —
come from the 143 accounts that have positive edge, net profit **and** at least ten
losing trades, counting a trader as followable when at least 80% of their orders
would place at that account size with no blocked exits.

Corrections are welcome. If a number here is wrong it gets fixed, not defended.
