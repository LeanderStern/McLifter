from pathlib import Path

from pydantic import validate_call


@validate_call
def shorten_path(path: Path, head: int = 3, tail: int = 2, ellipsis: str = "…") -> str:
    p = Path(path)
    rel = p.parts[1:] if p.anchor else p.parts
    if len(rel) <= head + tail:
        return str(p)
    shown = list(rel[:head]) + [ellipsis] + list(rel[-tail:])
    return p.anchor + "/".join(shown)