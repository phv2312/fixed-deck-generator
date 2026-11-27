class ETags:
    """Turn a slide revision into an ``ETag`` header and read it back from ``If-None-Match``."""

    @staticmethod
    def header_of(revision: str) -> str:
        """Return the quoted ``ETag`` value of ``revision``."""
        return f'"{revision}"'

    @staticmethod
    def revision_of(if_none_match: str | None) -> str | None:
        """Return the first revision in an ``If-None-Match`` value, or None when there is none.

        A browser sends the one tag that it holds, with or without the weak mark ``W/``.
        """
        if not if_none_match:
            return None
        first = if_none_match.split(",")[0].strip()
        return first.removeprefix("W/").strip('"') or None
