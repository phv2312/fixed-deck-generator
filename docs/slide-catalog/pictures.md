# pictures

[← All families](README.md)

Slides built around a picture.

| slide | preview & description | parameters |
|---|---|---|
| `figure` | <a href="images/pictures/figure.png"><img src="images/pictures/figure.png" alt="figure slide preview" width="480" loading="lazy"></a><br>Use this slide to present one picture across the full width, with a caption and a source. The picture carries its own labels and notes: the slide has no side text. Set bleed for a full-bleed photograph with the title in a dark band. | `title` (str, required): Slide headline.<br>`image` (str, required): Image file path or URL. A missing file renders a labelled placeholder.<br>`caption` (str | None, optional): Figure caption.<br>`source` (str | None, optional): Optional source line.<br>`bleed` (bool, optional, default: false): If true, the picture fills the whole slide and the title sits in a dark band at the bottom, with the caption below it. The source is not shown. |
| `screenshot` | <a href="images/pictures/screenshot.png"><img src="images/pictures/screenshot.png" alt="screenshot slide preview" width="480" loading="lazy"></a><br>Use this slide to present a screenshot in a browser frame. Numbered callouts explain each point. | `title` (str, required): Slide headline.<br>`image` (str, required): Image file path or URL. A missing file renders a labelled placeholder.<br>`callouts` (list[Callout], optional, default: []): Callouts, at most 8.<br>`callouts[].x` (float, required): Horizontal position inside the picture, 0 (left) to 1 (right).<br>`callouts[].y` (float, required): Vertical position inside the picture, 0 (top) to 1 (bottom).<br>`callouts[].text` (str, required): Callout text. |
