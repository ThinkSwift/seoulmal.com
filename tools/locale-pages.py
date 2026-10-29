#!/usr/bin/env python3
"""locale-pages — one static home page per language, the same output as ops web/locale-pages.py gives spriteer.com.

Google reads one language per URL, and this site translates in the browser. This writes /<lang>/index.html for every
language in js/strings.js with the copy filled in:
  - <html lang dir data-lang>, <title>, meta description, canonical, og:url/title/description in that language
  - hreflang for every language + x-default (the root) on every page, root included
  - <title> and description from the app's App Store listing (~/Projects/SeoulMal/fastlane/metadata/<locale>), as on
    the other sites: name — subtitle, and the promotional text
  - sitemap.xml lists every language URL
js/i18n.js reads data-lang first, so a language page stays in its language whatever the browser says.
Re-run after editing index.html, js/strings.js or the store listing:   python3 tools/locale-pages.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://seoulmal.com"
LISTING = os.path.expanduser("~/Projects/SeoulMal/fastlane/metadata")
ASC_LOCALE = {"es": "es-ES", "fr": "fr-FR", "de": "de-DE", "nl": "nl-NL", "ar": "ar-SA", "en": "en-US"}
HL_START, HL_END = "<!-- hreflang:start -->", "<!-- hreflang:end -->"

esc = lambda s: html.escape(s, quote=False)
attr = lambda s: html.escape(s, quote=True)


def fill(page, d):
    """Replace the text of <tag … data-i18n="key" …>text</tag> (text without child tags) with d[key]."""
    pat = re.compile(r'(<(\w+)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)([^<]*)(</\2>)')
    return pat.sub(lambda m: m.group(1) + esc(d[m.group(3)]) + m.group(5) if d.get(m.group(3)) and "{" not in d[m.group(3)]
                   else m.group(0), page)


def meta(page, name, value, prop=False):
    a = "property" if prop else "name"
    return re.sub(r'(<meta ' + a + r'="' + re.escape(name) + r'" content=")[^"]*(")', lambda m: m.group(1) + attr(value) + m.group(2),
                  page, count=1)


def head(page, lang, data_lang, title, desc, url, alternates):
    page = re.sub(r"<html[^>]*>", f'<html lang="{lang}"' + (f' data-lang="{data_lang}"' if data_lang else "")
                  + (' dir="rtl"' if lang == "ar" else "") + ">", page, count=1)
    page = re.sub(r"<title>.*?</title>", lambda m: f"<title>{esc(title)}</title>", page, count=1, flags=re.S)
    page = meta(page, "og:title", title, prop=True)
    page = meta(page, "description", desc)
    page = meta(page, "og:description", desc, prop=True)
    page = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', page, count=1)
    page = meta(page, "og:url", url, prop=True)
    block = HL_START + "\n" + "\n".join(f'  <link rel="alternate" hreflang="{h}" href="{u}">' for h, u in alternates) + "\n  " + HL_END
    return re.sub(re.escape(HL_START) + ".*?" + re.escape(HL_END), lambda m: block, page, count=1, flags=re.S)


def listing(lang):
    d = os.path.join(LISTING, ASC_LOCALE.get(lang, lang))
    read = lambda f: open(os.path.join(d, f), encoding="utf-8").read().strip() if os.path.isfile(os.path.join(d, f)) else ""
    return read("name.txt"), read("subtitle.txt"), read("promotional_text.txt")


def short(text, limit=170):
    out = ""
    for sent in re.split(r"(?<=[.!?。！？])\s*", text):
        if not sent:
            continue
        if len(out) + len(sent) > limit and out:
            break
        out = (out + " " + sent).strip() if out and not re.match(r"[぀-ヿ一-鿿]", sent) else out + sent
    return out[:limit]


def title_desc(lang, d):
    name, sub, promo = listing(lang)
    title = f"{name} — {sub}" if name and sub else d["page_title"]
    return title, short(promo) if promo else d["meta_desc"]


def main():
    src = open(os.path.join(ROOT, "js/strings.js"), encoding="utf-8").read()
    S = json.loads(src[src.index("{"):src.rindex("}") + 1])
    langs = [l for l in S if l != "en"]
    base = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    alts = [("en", ORIGIN + "/")] + [(l, f"{ORIGIN}/{l.lower()}/") for l in langs] + [("x-default", ORIGIN + "/")]
    t0, d0 = title_desc("en", S["en"])
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(head(base, "en", None, t0, d0, ORIGIN + "/", alts))
    for l in langs:
        d = {**S["en"], **S[l]}
        t1, d1 = title_desc(l, d)
        page = fill(head(base, l, l, t1, d1, f"{ORIGIN}/{l.lower()}/", alts), d)
        os.makedirs(os.path.join(ROOT, l.lower()), exist_ok=True)
        open(os.path.join(ROOT, l.lower(), "index.html"), "w", encoding="utf-8").write(page)
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    have = set(re.findall(r"<loc>([^<]+)</loc>", s))
    add = "".join(f"  <url><loc>{ORIGIN}/{l.lower()}/</loc></url>\n" for l in langs if f"{ORIGIN}/{l.lower()}/" not in have)
    open(p, "w", encoding="utf-8").write(s.replace("</urlset>", add + "</urlset>"))
    print(f"locale-pages: {len(langs)}/{len(langs)} language pages · sitemap +{len(add.splitlines())}")


if __name__ == "__main__":
    main()
