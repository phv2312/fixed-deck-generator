"""Checks that decide whether an SVG is displayable. v1 does not check the content."""

import re
import xml.etree.ElementTree as ET

from decks.visuals.models import Measurement, TextBox, VisualIssue
from decks.visuals.theme import TOKENS

MIN_FONT = 11.0
MAX_TEXTS = 40
MAX_SHAPES = 400
RATIO_TOLERANCE = 0.05
EDGE_TOLERANCE = 1.5
MIN_OVERLAP = 2.0

FORBIDDEN = frozenset({"script", "foreignobject", "iframe", "object", "embed", "audio", "video"})
SHAPES = frozenset({"rect", "circle", "ellipse", "path", "line", "polyline", "polygon"})
COLOR_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "color")
SAFE_COLORS = frozenset({"none", "currentcolor", "inherit", "transparent"})

_DECLARATION = re.compile(r"(fill|stroke|stop-color|flood-color|color)\s*:\s*([^;}]+)")
_HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
_FONT_SIZE = re.compile(r"font-size\s*:\s*([\d.]+)")
_CLASS = re.compile(r"^(fill|stroke)-(.+)$")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


class SvgChecker:
    """Check an SVG as text, then check its rendered measurements."""

    def static(self, svg: str, size: tuple[int, int]) -> list[VisualIssue]:
        """Check the SVG source. It needs no Chrome."""
        if re.search(r"<!(doctype|entity)", svg, re.IGNORECASE):
            return [self._error("unsafe_xml", "The SVG has a DOCTYPE or ENTITY.", "Remove it.")]
        try:
            root = ET.fromstring(svg.strip())
        except ET.ParseError as exc:
            return [self._error("xml_invalid", f"The SVG is not valid XML: {exc}.", "Fix it.")]
        if _local(root.tag) != "svg" or not root.get("viewBox"):
            return [self._error("bad_root", "The root must be <svg> with a viewBox.", "Add it.")]
        issues = self._ratio(root.get("viewBox", ""), size)
        elements = list(root.iter())
        for element in elements:
            issues += self._element(element)
        issues += self._limits(elements)
        return issues

    def geometry(self, measurement: Measurement, size: tuple[int, int]) -> list[VisualIssue]:
        """Check text boxes for clipping and overlap, and the picture for blankness."""
        issues: list[VisualIssue] = []
        if measurement.painted == 0:
            issues.append(
                self._error(
                    "blank_render", "Nothing visible is drawn.", "Draw shapes with token classes."
                )
            )
        width, height = size
        for box in measurement.boxes:
            outside = (
                box.x < -EDGE_TOLERANCE
                or box.y < -EDGE_TOLERANCE
                or box.x + box.w > width + EDGE_TOLERANCE
                or box.y + box.h > height + EDGE_TOLERANCE
            )
            if outside:
                issues.append(
                    self._error(
                        "text_clipped",
                        f"Text '{box.text[:30]}' leaves the frame ({box.x:.0f},{box.y:.0f},"
                        f"{box.w:.0f}x{box.h:.0f}) of {width}x{height}.",
                        "Move it inside, shorten it, or use text-anchor.",
                    )
                )
        issues += self._overlaps(measurement.boxes)
        return issues

    def _overlaps(self, boxes: list[TextBox]) -> list[VisualIssue]:
        issues: list[VisualIssue] = []
        for i, a in enumerate(boxes):
            for b in boxes[i + 1 :]:
                dx = min(a.x + a.w, b.x + b.w) - max(a.x, b.x)
                dy = min(a.y + a.h, b.y + b.h) - max(a.y, b.y)
                if dx > MIN_OVERLAP and dy > MIN_OVERLAP:
                    issues.append(
                        self._error(
                            "text_overlap",
                            f"Text '{a.text[:25]}' overlaps '{b.text[:25]}'.",
                            "Move one of them or shorten the labels.",
                        )
                    )
        return issues[:5]

    def _ratio(self, view_box: str, size: tuple[int, int]) -> list[VisualIssue]:
        parts = view_box.replace(",", " ").split()
        try:
            _, _, vw, vh = (float(p) for p in parts)
        except ValueError:
            return [self._error("bad_root", f"viewBox '{view_box}' is not 4 numbers.", "Fix it.")]
        if vw <= 0 or vh <= 0:
            return [self._error("bad_root", "viewBox has no size.", "Use a positive size.")]
        want = size[0] / size[1]
        if abs(vw / vh - want) / want > RATIO_TOLERANCE:
            return [
                self._error(
                    "wrong_ratio",
                    f"viewBox {vw:g}x{vh:g} does not match the {size[0]}x{size[1]} frame.",
                    f'Use viewBox="0 0 {size[0]} {size[1]}".',
                )
            ]
        return []

    def _element(self, element: ET.Element) -> list[VisualIssue]:
        tag = _local(element.tag)
        issues: list[VisualIssue] = []
        if tag in FORBIDDEN:
            issues.append(self._error("forbidden_element", f"<{tag}> is not allowed.", "Remove."))
        for name, value in element.attrib.items():
            key = _local(name)
            if key.startswith("on"):
                issues.append(self._error("forbidden_attr", f"Attribute {key} is not allowed.", ""))
            if key == "href" and not value.startswith("#"):
                issues.append(self._error("external_ref", f"href '{value[:40]}'.", "Remove it."))
            if key in COLOR_ATTRS:
                issues += self._color(value)
            if key == "style":
                issues += self._style(value)
            if key == "font-size":
                issues += self._font(value)
            if key == "class":
                issues += self._classes(value)
            if "url(" in value and "url(#" not in value:
                issues.append(self._error("external_ref", f"url() in {key}.", "Use url(#id)."))
        if tag == "style":
            issues += self._style(element.text or "")
            if "@import" in (element.text or ""):
                issues.append(self._error("external_ref", "@import is not allowed.", "Remove."))
        return issues

    def _color(self, value: str) -> list[VisualIssue]:
        text = value.strip().lower()
        if text in SAFE_COLORS or text.startswith(("var(", "url(#")):
            return []
        return [
            self._error(
                "color_literal",
                f"Colour '{value.strip()[:30]}' is not a theme token.",
                "Use class fill-<token> or stroke-<token> (accent, primary, light, tint, muted, "
                "grid, text, ink, bg).",
            )
        ]

    def _style(self, text: str) -> list[VisualIssue]:
        issues: list[VisualIssue] = []
        for _, value in _DECLARATION.findall(text):
            issues += self._color(value)
        literal = _HEX.search(text)
        if literal is not None and not issues:
            issues += self._color(literal.group(0))
        for size in _FONT_SIZE.findall(text):
            issues += self._font(size)
        return issues

    def _font(self, value: str) -> list[VisualIssue]:
        match = re.match(r"\s*([\d.]+)", value)
        if match is None or float(match.group(1)) >= MIN_FONT:
            return []
        return [
            self._error("font_too_small", f"Font size {value} is below {MIN_FONT:g}px.", "Raise.")
        ]

    def _classes(self, value: str) -> list[VisualIssue]:
        issues: list[VisualIssue] = []
        for name in value.split():
            match = _CLASS.match(name)
            if match is not None and match.group(2) not in TOKENS:
                issues.append(
                    self._error(
                        "unknown_token",
                        f"Class '{name}' uses an unknown token.",
                        f"Tokens: {', '.join(TOKENS)}.",
                    )
                )
        return issues

    def _limits(self, elements: list[ET.Element]) -> list[VisualIssue]:
        tags = [_local(e.tag) for e in elements]
        if not any(t in SHAPES or t == "text" for t in tags):
            return [self._error("empty_svg", "The SVG has no shape or text.", "Draw something.")]
        issues: list[VisualIssue] = []
        texts = tags.count("text")
        if texts > MAX_TEXTS:
            issues.append(
                self._warning("too_many_texts", f"{texts} texts; the limit is {MAX_TEXTS}.")
            )
        shapes = sum(1 for t in tags if t in SHAPES)
        if shapes > MAX_SHAPES:
            issues.append(self._warning("too_many_shapes", f"{shapes} shapes."))
        return issues

    def _error(self, code: str, message: str, suggestion: str) -> VisualIssue:
        return VisualIssue(code=code, severity="error", message=message, suggestion=suggestion)

    def _warning(self, code: str, message: str) -> VisualIssue:
        return VisualIssue(
            code=code, severity="warning", message=message, suggestion="Simplify the picture."
        )
