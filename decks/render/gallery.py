"""One self-contained gallery.html for reviewing every slide type, in both themes."""

import json
import re
from html import escape
from pathlib import Path
from typing import TypedDict, cast

from decks.builders import REGISTRY, build_deck
from decks.models.slides import DeckSpec
from decks.models.theme import THEMES as PALETTES

from .html import render_html

THEMES = tuple(PALETTES)


class GalleryEntry(TypedDict):
    """One gallery card: the slide, its metadata and both theme renders."""

    extra: str
    text: str
    family: str
    type: str
    n: int
    title: str
    html: dict[str, str]


def build_gallery(examples_dir: str = "examples") -> str:
    """Return the self-contained gallery HTML for every example slide."""
    entries: list[GalleryEntry] = []
    width = height = 0
    font = ""
    for f in sorted(Path(examples_dir).glob("*.json")):
        raw = json.loads(f.read_text())
        per_theme: dict[str, list[str]] = {}
        for theme in THEMES:
            data = {**raw, "theme": theme}
            deck = build_deck(DeckSpec.model_validate(data))
            fragments, width, height, font = render_html(deck, fragments=True)
            per_theme[theme] = cast(list[str], fragments)
        for i, spec in enumerate(raw["slides"]):
            kind = spec["type"]
            chart = spec.get("chart")
            extra = chart.get("type", "") if isinstance(chart, dict) else ""
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", per_theme["green"][i]))
            entries.append(
                {
                    "extra": extra,
                    "text": text,
                    "family": REGISTRY[kind].family,
                    "type": kind,
                    "n": i + 1,
                    "title": str(
                        spec.get("title") or spec.get("question") or spec.get("text") or kind
                    )[:90],
                    "html": {t: per_theme[t][i] for t in THEMES},
                }
            )
    families: dict[str, dict[str, int]] = {}
    for e in entries:
        families.setdefault(e["family"], {}).setdefault(e["type"], 0)
        families[e["family"]][e["type"]] += 1

    cards = "".join(
        f'<article class="card" data-family="{e["family"]}" data-type="{e["type"]}" '
        f'data-search="{escape((e["family"] + " " + e["type"] + " " + e["extra"] + " " + e["title"] + " " + e["text"]).lower())}">'
        f'<div class="thumb">'
        + "".join(f'<div class="frame t-{t}">{e["html"][t]}</div>' for t in THEMES)
        + "</div>"
        f'<div class="meta"><b>{e["type"]}</b> <span>#{e["n"]} · {e["family"]}{(" · " + e["extra"]) if e["extra"] else ""}</span><em>{escape(e["title"])}</em></div></article>'
        for e in entries
    )
    nav = "".join(
        f'<div class="fam"><a href="#" data-f="{fam}" class="famlink">{fam} <small>{sum(types.values())}</small></a>'
        + "".join(
            f'<a href="#" data-t="{t}" class="typelink">{t} <small>{n}</small></a>'
            for t, n in types.items()
        )
        + "</div>"
        for fam, types in families.items()
    )
    total = len(entries)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Slide gallery</title><style>
:root{{--bg:#f4f5f7;--fg:#1f2937;--mut:#6b7280;--card:#fff;--line:#e5e7eb;--acc:#0b3d2e;--side:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16181d;--fg:#e5e7eb;--mut:#9ca3af;--card:#1f2229;--line:#2f333b;--acc:#7fd6b4;--side:#1b1e24}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{position:sticky;top:0;z-index:5;display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:10px 16px;background:var(--side);border-bottom:1px solid var(--line)}}
header h1{{font-size:16px;margin:0 8px 0 0}}header input[type=search]{{flex:1;min-width:160px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}}
.seg{{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}}.seg button{{border:0;background:transparent;color:var(--fg);padding:7px 12px;cursor:pointer}}
.seg button.on{{background:var(--acc);color:var(--bg)}}label.z{{display:flex;gap:6px;align-items:center;color:var(--mut)}}
.layout{{display:flex;align-items:flex-start}}nav{{position:sticky;top:57px;width:210px;max-height:calc(100vh - 57px);overflow:auto;padding:12px;background:var(--side);border-right:1px solid var(--line);flex:none}}
nav a{{display:flex;justify-content:space-between;color:var(--fg);text-decoration:none;padding:3px 8px;border-radius:6px}}nav a:hover{{background:var(--bg)}}
nav a.on{{background:var(--acc);color:var(--bg)}}nav .famlink{{font-weight:700;margin-top:8px}}nav .typelink{{padding-left:20px;color:var(--mut)}}nav .typelink.on{{color:var(--bg)}}nav small{{opacity:.7}}
main{{flex:1;min-width:0;padding:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(var(--cw,360px),1fr));gap:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;cursor:zoom-in}}
.thumb{{position:relative;width:100%;aspect-ratio:{width}/{height};overflow:hidden;background:#fff}}
.frame{{position:absolute;left:0;top:0;width:{width}px;height:{height}px;transform-origin:0 0;display:none}}
body.green .t-green,body.orange .t-orange{{display:block}}
.slide{{position:absolute;left:0;top:0;width:{width}px;height:{height}px;overflow:hidden;font-family:{font};background:#fff}}
.e{{position:absolute;margin:0}}.g{{position:absolute;left:0;top:0}}table.e{{border-collapse:collapse}}th,td{{border:1px solid #d1d5db;padding:6px 10px}}
.meta{{padding:8px 12px;display:flex;flex-wrap:wrap;gap:2px 8px;align-items:baseline}}.meta span{{color:var(--mut);font-size:12px}}.meta em{{flex-basis:100%;color:var(--mut);font-style:normal;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.empty{{padding:40px;color:var(--mut);text-align:center;display:none}}
#lb{{position:fixed;inset:0;background:rgba(0,0,0,.86);display:none;z-index:20;align-items:center;justify-content:center;flex-direction:column;gap:10px}}
#lb.open{{display:flex}}#lbbox{{position:relative;overflow:hidden;background:#fff;border-radius:6px}}#lbbox .frame{{display:none}}
body.green #lbbox .t-green,body.orange #lbbox .t-orange{{display:block}}#lbcap{{color:#e5e7eb;font-size:13px}}
</style></head><body class="green"><header><h1>Slide gallery</h1>
<input id="q" type="search" placeholder="Search type, family or title…  ({total} slides)">
<span class="seg" id="theme"><button data-th="green" class="on">green</button><button data-th="orange">orange</button></span>
<label class="z">Size <input id="zoom" type="range" min="220" max="720" value="360"></label><span id="count" style="color:var(--mut)"></span></header>
<div class="layout"><nav><a href="#" class="famlink on" data-f="">All <small>{total}</small></a>{nav}</nav>
<main><div class="grid" id="grid">{cards}</div><div class="empty" id="empty">No slide matches.</div></main></div>
<div id="lb"><div id="lbbox"></div><div id="lbcap"></div></div>
<script>
const W={width},H={height};const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
let fam='',typ='',q='';
function scaleThumbs(){{$$('.thumb').forEach(t=>{{const k=t.clientWidth/W;t.querySelectorAll('.frame').forEach(f=>f.style.transform='scale('+k+')')}})}}
function apply(){{let n=0;$$('.card').forEach(c=>{{const ok=(!fam||c.dataset.family===fam)&&(!typ||c.dataset.type===typ)&&(!q||c.dataset.search.includes(q));c.style.display=ok?'':'none';if(ok)n++}});
$('#count').textContent=n+' shown';$('#empty').style.display=n?'none':'block';scaleThumbs()}}
$('#q').addEventListener('input',e=>{{q=e.target.value.toLowerCase().trim();apply()}});
$$('#theme button').forEach(b=>b.onclick=()=>{{document.body.className=b.dataset.th;$$('#theme button').forEach(x=>x.classList.toggle('on',x===b));try{{localStorage.setItem('gtheme',b.dataset.th)}}catch(e){{}}if($('#lb').classList.contains('open'))show(cur)}});
$('#zoom').addEventListener('input',e=>{{$('#grid').style.setProperty('--cw',e.target.value+'px');scaleThumbs()}});
$$('nav a').forEach(a=>a.onclick=e=>{{e.preventDefault();fam=a.dataset.f||'';typ=a.dataset.t||'';if(a.dataset.t){{const p=a.parentElement.querySelector('.famlink');fam=p.dataset.f}}$$('nav a').forEach(x=>x.classList.remove('on'));a.classList.add('on');apply();scrollTo(0,0)}});
let cur=0;function visible(){{return $$('.card').filter(c=>c.style.display!=='none')}}
function show(i){{const v=visible();if(!v.length)return;cur=(i+v.length)%v.length;const c=v[cur];const box=$('#lbbox');const k=Math.min((innerWidth-60)/W,(innerHeight-90)/H);
box.style.width=W*k+'px';box.style.height=H*k+'px';box.innerHTML=c.querySelector('.thumb').innerHTML;box.querySelectorAll('.frame').forEach(f=>f.style.transform='scale('+k+')');
$('#lbcap').textContent=c.querySelector('.meta b').textContent+' · '+c.querySelector('.meta em').textContent+'   ('+(cur+1)+'/'+v.length+')';$('#lb').classList.add('open')}}
$$('.card').forEach(c=>c.onclick=()=>show(visible().indexOf(c)));
$('#lb').onclick=e=>{{if(e.target.id==='lb')$('#lb').classList.remove('open')}};
addEventListener('keydown',e=>{{if(!$('#lb').classList.contains('open'))return;if(e.key==='Escape')$('#lb').classList.remove('open');if(e.key==='ArrowRight')show(cur+1);if(e.key==='ArrowLeft')show(cur-1);if(e.key==='t'){{$$('#theme button')[document.body.className==='green'?1:0].click()}}}});
addEventListener('resize',()=>{{scaleThumbs();if($('#lb').classList.contains('open'))show(cur)}});
try{{const t=localStorage.getItem('gtheme');if(t)$$('#theme button').find(b=>b.dataset.th===t)?.click()}}catch(e){{}}
apply();
</script></body></html>"""
