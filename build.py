"""Turn essay.md into the web page (index.html).

Edit essay.md, then run:  python3 build.py
Only the small set of Markdown used in the essay is supported,
plus "!> " lines right after the title, which become the opening note.
"""
import html
import re
import sys
from pathlib import Path

SRC = Path(__file__).with_name("essay.md")
OUT = Path(__file__).with_name("index.html")
AUTHOR = "Elamurugu Kandasamy"
DATE = "November 2026"


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def convert(md):
    lines = md.strip().splitlines()
    title = lines[0].lstrip("# ").strip()
    dek = lines[2].strip("* ") if len(lines) > 2 and lines[2].startswith("**") else ""
    body = lines[3:] if dek else lines[1:]
    while body and not body[0].strip():
        body = body[1:]
    note = []
    while body and body[0].startswith("!> "):
        note.append(inline(body.pop(0)[3:]))

    out, block, kind = [], [], None
    in_section = False

    def flush():
        nonlocal block, kind
        if not block:
            return
        if kind == "quote":
            out.append("<blockquote><p>" + "<br>".join(inline(l) for l in block) + "</p></blockquote>")
        elif kind == "list":
            out.append("<ul>" + "".join(f"<li>{inline(l)}</li>" for l in block) + "</ul>")
        else:
            text = "<br>".join(inline(l) for l in block)
            if len(block) == 1 and block[0].startswith("*") and not block[0].startswith("**"):
                out.append(f'<p class="signoff">{text}</p>')
            else:
                out.append(f"<p>{text}</p>")
        block, kind = [], None

    for raw in body:
        line = raw.rstrip()
        if not line:
            flush()
            continue
        if line == "---":
            flush()
            out.append('<hr aria-hidden="true">')
            continue
        if line.startswith("## "):
            flush()
            if in_section:
                out.append("</section>")
            heading = line[3:]
            out.append(f'<section id="{slug(heading)}"><h2>{inline(heading)}</h2>')
            in_section = True
            continue
        if line.startswith("### "):
            flush()
            out.append(f"<h3>{inline(line[4:])}</h3>")
            continue
        new_kind = "quote" if line.startswith("> ") else "list" if line.startswith("- ") else "para"
        if kind and new_kind != kind:
            flush()
        kind = new_kind
        block.append(line[2:] if new_kind in ("quote", "list") else line)
    flush()
    if in_section:
        out.append("</section>")
    note_html = f'<aside class="note"><p>{"<br>".join(note)}</p></aside>' if note else ""
    return title, dek, note_html, "\n".join(out)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>The Golden Cage</title>
<meta name="description" content="{dek}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one quiet reading column; the only ornament is a set of thin brass "bars" behind the title. */
:root {{
  --paper: #f4f4f1;
  --ink: #1c1e23;
  --muted: #5e6068;
  --rule: #d9d8d2;
  --brass: #8a6a1f;
  --brass-soft: rgba(138, 106, 31, 0.16);
  --display: "Young Serif", Georgia, "Times New Roman", serif;
  --body: "Literata", Georgia, "Times New Roman", serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #15171b; --ink: #e7e5df; --muted: #a2a2a8; --rule: #2c2e34;
    --brass: #d2b062; --brass-soft: rgba(210, 176, 98, 0.14); color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper: #15171b; --ink: #e7e5df; --muted: #a2a2a8; --rule: #2c2e34;
  --brass: #d2b062; --brass-soft: rgba(210, 176, 98, 0.14); color-scheme: dark;
}}
body {{
  background: var(--paper);
  color: var(--ink);
  font-family: var(--body);
  margin: 0;
  font-size: clamp(1.125rem, 1rem + 0.4vw, 1.3rem);
  line-height: 1.7;
  -webkit-text-size-adjust: 100%;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}}
.wrap {{ max-width: 44rem; margin: 0 auto; padding-block: 0 5rem; }}

header {{ position: relative; padding-block: 5rem 3rem; }}
header::before {{
  content: ""; position: absolute; inset: 0 -2rem; z-index: 0; pointer-events: none;
  background: repeating-linear-gradient(90deg, transparent 0 2.4rem, var(--brass-soft) 2.4rem calc(2.4rem + 1px));
  -webkit-mask-image: linear-gradient(180deg, #000 0%, transparent 95%);
          mask-image: linear-gradient(180deg, #000 0%, transparent 95%);
}}
header > * {{ position: relative; z-index: 1; }}
.kicker {{
  font-family: var(--mono); font-size: 0.75rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--brass); margin: 0 0 1.25rem;
}}
h1 {{
  font-family: var(--display); font-weight: 400;
  font-size: clamp(2.75rem, 9vw, 4.5rem); line-height: 1.02;
  letter-spacing: -0.01em; margin: 0 0 1.25rem; text-wrap: balance;
}}
.dek {{ font-size: 1.25rem; line-height: 1.5; color: var(--muted); margin: 0; text-wrap: balance; }}
.dek strong {{ font-weight: 400; }}
.dek em {{ color: var(--brass); }}
.note {{
  margin-top: 2.25rem; padding: 0.9rem 1rem;
  border: 1px dashed var(--brass); border-radius: 2px;
  font-size: 0.95rem; line-height: 1.6; color: var(--muted); background: var(--paper);
}}
.note p {{ margin: 0; }}

article p {{ margin: 0 0 1.15rem; }}
h2 {{
  font-family: var(--display); font-weight: 400; font-size: 1.85rem;
  line-height: 1.2; margin: 0.5rem 0 1.25rem; text-wrap: balance;
}}
h3 {{
  font-family: var(--mono); font-weight: 500; font-size: 0.8rem;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--brass);
  margin: 2.5rem 0 0.75rem;
}}
strong {{ font-weight: 600; }}
blockquote {{
  margin: 1.75rem 0; padding: 0.25rem 0 0.25rem 1.25rem;
  border-left: 2px solid var(--brass);
  font-family: var(--display); font-size: 1.3rem; line-height: 1.45;
}}
blockquote p {{ margin: 0; }}
ul {{ padding-left: 1.2rem; margin: 0 0 1.25rem; }}
li {{ margin-bottom: 0.5rem; }}
li::marker {{ color: var(--brass); }}
hr {{ border: 0; margin: 3rem 0; text-align: center; }}
hr::after {{ content: "|  |  |"; font-family: var(--mono); color: var(--brass); letter-spacing: 0.3em; }}

/* The one line the whole essay turns on gets room to breathe. */
#the-difference-in-one-line {{ text-align: center; padding-block: 1rem; }}
#the-difference-in-one-line h2 {{
  font-family: var(--mono); font-size: 0.8rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--brass);
}}
#the-difference-in-one-line p:first-of-type {{
  font-family: var(--display); font-size: clamp(1.6rem, 5vw, 2.1rem); line-height: 1.25; text-wrap: balance;
}}
#the-difference-in-one-line p:first-of-type strong {{ font-weight: 400; }}
#the-difference-in-one-line p:last-of-type {{ color: var(--muted); }}

#last-thought p {{ font-family: var(--display); font-size: 1.35rem; line-height: 1.45; }}
.signoff {{ color: var(--muted); font-size: 1rem; }}
.signoff em {{ font-style: italic; }}

footer {{
  border-top: 1px solid var(--rule); padding-top: 1.25rem; margin-top: 3rem;
  font-family: var(--mono); font-size: 0.75rem; color: var(--muted); letter-spacing: 0.04em;
}}
@media (max-width: 480px) {{
  header {{ padding-block: 3.5rem 2rem; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="kicker">An essay by {author} &middot; {date}</p>
    <h1>{title}</h1>
    <p class="dek">{dek_html}</p>
    {note}
  </header>
  <article>
{body}
  </article>
  <footer>{author} &middot; {date}</footer>
</div>
</body>
</html>
"""


def main():
    title, dek, note, body = convert(SRC.read_text(encoding="utf-8"))
    OUT.write_text(
        TEMPLATE.format(
            title=html.escape(title), dek=html.escape(dek.replace("*", "")), dek_html=inline(dek),
            note=note, body=body, author=AUTHOR, date=DATE,
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
