#!/usr/bin/env python3
"""แปลง manual_site/docs/*.md เป็น public/index.html หน้าเดียว (สารบัญ + ปุ่ม copy) เรียกผ่าน build.sh"""
import base64, html, re, sys, unicodedata
from pathlib import Path
import markdown

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    HAVE_PYG = True
except Exception:
    HAVE_PYG = False

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TITLE = "AI Camp: ROS 2 + MQTT"
SUBTITLE = "คู่มือนักเรียน"

FONTS = Path(__file__).resolve().parent / "fonts"


def font_css():
    """ฝังฟอนต์ IBM Plex Sans Thai (tools/fonts/) ลงใน HTML เปิดแบบออฟไลน์ก็ได้ฟอนต์เดียวกัน"""
    css = (FONTS / "fonts.css").read_text(encoding="utf-8")
    def embed(m):
        data = base64.b64encode((FONTS / m.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"
    return re.sub(r"url\(([\w.-]+\.woff2)\)", embed, css)


LANG_LABEL = {"bash": "คำสั่ง", "cpp": "C++", "c": "C", "python": "Python", "ini": "platformio.ini"}


def slug(text):
    text = unicodedata.normalize("NFKC", text).strip().lower()
    out = []
    for ch in text:
        if ch.isalnum() or unicodedata.category(ch).startswith("M"):
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    return re.sub(r"-+", "-", "".join(out)).strip("-") or "section"


def chapter_files():
    files = sorted(DOCS.glob("[0-9][0-9]-*.md"))
    ts = DOCS / "troubleshooting.md"
    if ts.exists():
        files.append(ts)
    return files


def preprocess(src):
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)          # ซ่อนหมายเหตุผู้สอน
    src = src.replace("<details>", '<details markdown="1">')
    # ```text ที่ตามหลังบรรทัด "ผลลัพธ์" = output, ที่เหลือ = แผนภาพ
    lines = src.split("\n")
    out, last_text = [], ""
    for ln in lines:
        if ln.startswith("```text"):
            ln = "```output" if "ผลลัพธ์" in last_text else "```diagram"
        if ln.strip() and not ln.startswith("```"):
            last_text = ln
        out.append(ln)
    return "\n".join(out)


def render_code(m):
    lang = m.group(1)
    code = html.unescape(m.group(2))
    raw = html.escape(code, quote=True)
    if lang == "output":
        kind, label, body = "out", "ผลลัพธ์ที่ควรเห็น", html.escape(code)
        copy = ""
    elif lang == "diagram":
        return f'<pre class="diagram"><code>{html.escape(code)}</code></pre>'
    else:
        kind = "in" if lang == "bash" else "src"
        label = LANG_LABEL.get(lang, lang)
        if lang == "bash":
            label = "พิมพ์คำสั่งนี้"
        body = html.escape(code)
        if HAVE_PYG:
            try:
                body = highlight(code, get_lexer_by_name(lang), HtmlFormatter(nowrap=True))
            except Exception:
                pass
        copy = f'<button class="copy" type="button" data-code="{raw}" aria-label="คัดลอก">คัดลอก</button>'
    return (f'<div class="code {kind}"><div class="code-head"><span class="code-label">{label}</span>{copy}</div>'
            f'<pre><code>{body.rstrip()}</code></pre></div>')


def build():
    files = chapter_files()
    explicit_ids = set()
    for f in files:
        explicit_ids.update(re.findall(r'<a id="([^"]+)"', f.read_text(encoding="utf-8")))
    stems = {f.name: f.stem for f in files}

    chapters = []
    for f in files:
        stem = f.stem
        md = markdown.Markdown(
            extensions=["tables", "fenced_code", "md_in_html", "attr_list", "sane_lists", "toc"],
            extension_configs={"toc": {"slugify": lambda v, sep, s=stem: f"{s}--{slug(v)}", "toc_depth": "2-3"}},
        )
        body = md.convert(preprocess(f.read_text(encoding="utf-8")))
        title = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title_txt = re.sub(r"<[^>]+>", "", title.group(1)) if title else stem

        body = re.sub(r'<pre><code class="language-(\w+)">(.*?)</code></pre>', render_code, body, flags=re.S)

        def fix_link(m):
            name, frag = m.group(1), m.group(2) or ""
            if name not in stems:
                return m.group(0)
            if not frag:
                return f'href="#{stems[name]}"'
            fid = frag[1:]
            return f'href="#{fid if fid in explicit_ids else stems[name] + "--" + fid}"'
        body = re.sub(r'href="([\w.\-]+\.md)(#[^"]*)?"', fix_link, body)
        # ลิงก์ไปไฟล์โค้ด (../firmware/...) ใช้บนเว็บไม่ได้ -> แสดงเป็นชื่อไฟล์แทน
        body = re.sub(r'<a href="\.\./[^"]*">(.*?)</a>',
                      lambda m: m.group(1) if m.group(1).startswith("<code>") else f"<code>{m.group(1)}</code>", body)
        body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
        body = body.replace("<a href=\"http", "<a target=\"_blank\" rel=\"noopener\" href=\"http")
        # โครง h2 สำหรับสารบัญ
        h2s = []
        for t in md.toc_tokens:
            for c in (t["children"] if t["level"] == 1 else [t]):
                if c["level"] == 2:
                    h2s.append((c["id"], re.sub(r"<[^>]+>", "", html.unescape(c["name"]))))
        chapters.append(dict(stem=stem, title=title_txt, body=body, h2=h2s))
    return chapters


def page(chapters, print_mode=False):
    nav = []
    for c in chapters:
        subs = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n in c["h2"])
        nav.append(f'<li class="ch" data-ch="{c["stem"]}"><a class="ch-link" href="#{c["stem"]}">{html.escape(c["title"])}</a>'
                   f'<ul class="subs">{subs}</ul></li>')
    secs = []
    for n, c in enumerate(chapters):
        prev_l = f'<a href="#{chapters[n-1]["stem"]}">← {html.escape(chapters[n-1]["title"])}</a>' if n else "<span></span>"
        next_l = f'<a href="#{chapters[n+1]["stem"]}">{html.escape(chapters[n+1]["title"])} →</a>' if n + 1 < len(chapters) else "<span></span>"
        body = c["body"]
        secs.append(f'<section class="chapter" id="{c["stem"]}" data-ch="{c["stem"]}">{body}<nav class="pager">{prev_l}{next_l}</nav></section>')
    css = font_css() + (Path(__file__).parent / "manual.css").read_text(encoding="utf-8")
    js = (Path(__file__).parent / "manual.js").read_text(encoding="utf-8")
    details_fix = "<script>document.querySelectorAll('details').forEach(d=>d.open=true)</script>" if print_mode else ""
    return f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} — {SUBTITLE}</title>
<style>{css}</style></head>
<body class="{'print' if print_mode else ''}">
<header class="topbar"><button id="menu" aria-label="เปิดสารบัญ">☰</button><strong>{TITLE}</strong></header>
<aside id="sidebar"><div class="brand"><div class="brand-t">{TITLE}</div><div class="brand-s">{SUBTITLE}</div></div>
<ol class="toc">{''.join(nav)}</ol>
<div class="legend"><span class="sw in"></span>คำสั่งที่พิมพ์ <span class="sw out"></span>ผลลัพธ์</div></aside>
<div id="scrim"></div>
<main>
<div class="cover"><h1 class="cover-t">{TITLE}</h1><p>{SUBTITLE}</p></div>
{''.join(secs)}
</main>
<script>{js}</script>{details_fix}
</body></html>"""


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "public"
    out.mkdir(parents=True, exist_ok=True)
    chapters = build()
    (out / "index.html").write_text(page(chapters), encoding="utf-8")
    print(f"สร้าง {out/'index.html'} ({len(chapters)} บท)")


if __name__ == "__main__":
    main()
