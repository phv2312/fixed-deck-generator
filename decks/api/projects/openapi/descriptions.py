from typing import ClassVar

from decks.api.openapi import RouteDoc


class ProjectDocs:
    """Swagger text of the project endpoints."""

    LIST: ClassVar[RouteDoc] = RouteDoc(
        "List projects",
        "Return one page of projects. The project that changed last comes first.",
    )
    CREATE: ClassVar[RouteDoc] = RouteDoc(
        "Create a project",
        "Create an empty project in the `draft` phase. The server makes the project id.",
    )
    READ: ClassVar[RouteDoc] = RouteDoc(
        "Read a project",
        "Return the name, the phase, the slide count, and the thumbnail of one project.",
    )
    DELETE: ClassVar[RouteDoc] = RouteDoc(
        "Delete a project",
        "Delete the project and all its files. A running chat turn blocks the delete.",
    )
    SLIDE_HTML: ClassVar[RouteDoc] = RouteDoc(
        "Read a slide as HTML",
        "Return a self-contained HTML page that shows one slide of the built deck. "
        "The page scales to the width of its frame, so it fits in an `iframe`.",
    )
