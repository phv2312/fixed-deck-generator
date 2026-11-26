from pathlib import Path
from typing import ClassVar

from decks.api.payloads import PageResponse
from decks.api.projects.payloads import ProjectResponse

EXAMPLES = Path(__file__).parent / "examples"


class ProjectExamples:
    """Response examples of the project endpoints. A wrong example fails at import."""

    READ: ClassVar[ProjectResponse] = ProjectResponse.model_validate_json(
        (EXAMPLES / "project.json").read_text()
    )
    LIST: ClassVar[PageResponse[ProjectResponse]] = PageResponse[
        ProjectResponse
    ].model_validate_json((EXAMPLES / "project_page.json").read_text())
