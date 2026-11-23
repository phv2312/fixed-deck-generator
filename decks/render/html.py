"""Stage 2: Deck -> self-contained HTML (absolute-positioned elements)."""

from html import escape

from decks.design import LINE_HEIGHT, MONO_FONT
from decks.models.elements import BULLET, Chart, Group, Image, Line, Polygon, Shape, Table, Text
from decks.models.slides import Deck


def img_src(src: str) -> str:
    """Inline local image files as data URIs so the HTML stays self-contained."""
    import base64
    import mimetypes
    from pathlib import Path

    if src.startswith(("http://", "https://", "data:")):
        return src
    p = Path(src)
    if p.is_file():
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
    return src


def text_html(text: str) -> str:
    """Escape ``text``. A bullet line gets a 1em marker so its wrapped lines hang under its text."""
    if BULLET not in text:
        return escape(text)
    lines = []
    for line in text.split("\n"):
        if line.startswith(BULLET):
            marker = '<span style="display:inline-block;width:1em;text-indent:0">&bull;</span>'
            lines.append(
                f'<div style="padding-left:1em;text-indent:-1em">{marker}{escape(line[len(BULLET) :])}</div>'
            )
        else:
            lines.append(f"<div>{escape(line)}</div>")
    return f"<div>{''.join(lines)}</div>"


ALIGN = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}
JUSTIFY = {"left": "flex-start", "center": "center", "right": "flex-end"}


def render_html(deck: Deck, fragments: bool = False):
    """Full HTML document, or (fragments=True) one <section class="slide"> string per slide."""

    def c(v: str | None) -> str:
        return "none" if v is None else deck.palette.get(v, v)

    def box(e, extra: str = "") -> str:
        return f"left:{e.x:g}px;top:{e.y:g}px;width:{e.w:g}px;height:{e.h:g}px;{extra}"

    def el(e) -> str:
        if isinstance(e, Text):
            face = f"font-family:{MONO_FONT};" if e.mono else ""
            face += "font-style:italic;" if e.italic else ""
            face += "text-decoration:underline;" if e.underline else ""
            face += f"font-family:{e.font_family};" if e.font_family else ""
            st = box(
                e,
                f"font-size:{e.font_size:g}px;color:{c(e.color)};"
                f"font-weight:{700 if e.bold else 400};{face}"
                f"display:flex;white-space:pre-line;line-height:{LINE_HEIGHT};"
                f"align-items:{ALIGN[e.valign]};justify-content:{JUSTIFY[e.align]};"
                f"text-align:{e.align};",
            )
            return f'<div class="e" style="{st}">{text_html(e.text)}</div>'
        if isinstance(e, Shape):
            st = box(e, f"background:{c(e.fill)};opacity:{e.opacity};box-sizing:border-box;")
            if e.stroke:
                st += (
                    f"border:{e.stroke_width:g}px {'dashed' if e.dash else 'solid'} {c(e.stroke)};"
                )
            if e.shape == "ellipse":
                st += "border-radius:50%;"
            elif e.radius:
                st += f"border-radius:{e.radius:g}px;"
            return f'<div class="e" style="{st}"></div>'
        if isinstance(e, Line):
            d = ' stroke-dasharray="6 5"' if e.dash else ""
            mk = ""
            if e.arrow:
                mid = f"ah{abs(hash((e.x1, e.y1, e.x2, e.y2)))}"
                mk = (
                    f'<defs><marker id="{mid}" markerWidth="6" markerHeight="6" refX="5" refY="3" '
                    f'orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="{c(e.color)}"/></marker></defs>'
                )
                d += f' marker-end="url(#{mid})"'
            return (
                f'<svg class="e" width="{deck.width}" height="{deck.height}">{mk}'
                f'<line x1="{e.x1:g}" y1="{e.y1:g}" x2="{e.x2:g}" y2="{e.y2:g}" '
                f'stroke="{c(e.color)}" stroke-width="{e.width:g}"{d}/></svg>'
            )
        if isinstance(e, Polygon):
            pts = " ".join(f"{x:g},{y:g}" for x, y in e.points)
            d = ' stroke-dasharray="7 5"' if e.dash else ""
            return (
                f'<svg class="e" width="{deck.width}" height="{deck.height}">'
                f'<polygon points="{pts}" fill="{c(e.fill)}" stroke="{c(e.stroke)}" '
                f'stroke-width="{e.stroke_width:g}" opacity="{e.opacity}"{d}/></svg>'
            )
        if isinstance(e, Image):
            return (
                f'<img class="e" style="{box(e)}object-fit:{e.fit}" src="{escape(img_src(e.src))}">'
            )
        if isinstance(e, Table):
            rows = ""
            for i, r in enumerate(e.rows):
                tag = "th" if (e.header and i == 0) else "td"
                rows += "<tr>" + "".join(f"<{tag}>{escape(x)}</{tag}>" for x in r) + "</tr>"
            return (
                f'<table class="e" style="{box(e, f"font-size:{e.font_size:g}px;")}">{rows}</table>'
            )
        if isinstance(e, Group):
            return f'<div class="g" data-name="{escape(e.name)}">{"".join(el(x) for x in e.children)}</div>'
        if isinstance(e, Chart):
            return f'<div class="e" style="{box(e)}border:1px dashed #999">chart: {e.kind}</div>'
        raise TypeError(type(e))

    parts = [
        f'<section class="slide" data-family="{s.family}" data-kind="{s.kind}">{"".join(el(e) for e in s.elements)}'
        f'<div class="e" style="right:32px;bottom:20px;font-size:12px;color:{c("muted")}">{i}</div>'
        f"</section>"
        for i, s in enumerate(deck.slides, 1)
    ]
    if fragments:
        return parts, deck.width, deck.height, deck.font
    slides = "".join(parts)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Deck</title><style>
body{{margin:0;background:#2b2f36;font-family:{deck.font}}}
.wrap{{display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px 0}}
.frame{{position:relative}}
.slide{{position:absolute;left:0;top:0;width:{deck.width}px;height:{deck.height}px;
background:{c("bg")};overflow:hidden;transform-origin:0 0}}
.e{{position:absolute;margin:0}} .g{{position:absolute;left:0;top:0}}
table.e{{border-collapse:collapse}} th,td{{border:1px solid {c("grid")};padding:6px 10px}}
@media print{{body{{background:none}}.wrap{{padding:0;gap:0}}.frame{{width:{deck.width}px!important;height:{deck.height}px!important}}
.slide{{transform:none!important}}@page{{size:{deck.width}px {deck.height}px;margin:0}}}}
</style></head><body><div class="wrap">{slides}</div><script>
const W={deck.width},H={deck.height};
function fit(){{const s=Math.min(1,(innerWidth-48)/W);
document.querySelectorAll('.slide').forEach(el=>{{
if(!el.parentElement.classList.contains('frame')){{const f=document.createElement('div');
f.className='frame';el.replaceWith(f);f.appendChild(el);}}
el.style.transform='scale('+s+')';el.parentElement.style.width=W*s+'px';el.parentElement.style.height=H*s+'px';}});}}
addEventListener('resize',fit);fit();
</script></body></html>"""
