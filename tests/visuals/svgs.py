"""SVG fixtures shared by the visual tests."""

GOOD = """<svg viewBox="0 0 1152 440" xmlns="http://www.w3.org/2000/svg">
<rect x="40" y="60" width="120" height="260" class="fill-accent"/>
<rect x="200" y="140" width="120" height="180" class="fill-light"/>
<line x1="30" y1="320" x2="1100" y2="320" class="stroke-grid" stroke-width="2"/>
<text x="40" y="350" font-size="14" class="fill-muted">Q1</text>
<text x="200" y="350" font-size="14" class="fill-muted">Q2</text></svg>"""

HEX_COLOR = GOOD.replace('class="fill-light"', 'fill="#3B82F6"')
STYLE_COLOR = GOOD.replace('class="fill-light"', 'style="fill: rgb(1,2,3)"')
UNKNOWN_TOKEN = GOOD.replace("fill-light", "fill-blue")
SCRIPT = GOOD.replace("</svg>", "<script>alert(1)</script></svg>")
FOREIGN = GOOD.replace("</svg>", "<foreignObject/></svg>")
EVENT = GOOD.replace("<rect ", '<rect onclick="x()" ', 1)
EXTERNAL = GOOD.replace("</svg>", '<image href="http://x.test/a.png"/></svg>')
DOCTYPE = '<!DOCTYPE svg [<!ENTITY a "b">]>' + GOOD
SMALL_FONT = GOOD.replace('font-size="14"', 'font-size="9"', 1)
WRONG_RATIO = GOOD.replace('viewBox="0 0 1152 440"', 'viewBox="0 0 100 100"')
NO_VIEWBOX = GOOD.replace(' viewBox="0 0 1152 440"', "")
NOT_XML = "<svg viewBox='0 0 1152 440'><rect></svg>"
EMPTY = '<svg viewBox="0 0 1152 440" xmlns="http://www.w3.org/2000/svg"><defs/></svg>'
CLIPPED = GOOD.replace('x="200" y="350"', 'x="1140" y="350"')
