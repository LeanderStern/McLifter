from pathlib import Path
from typing import Annotated

from pydantic import StringConstraints
from pydantic.types import PathType

Base62Str = Annotated[str, StringConstraints(pattern=r"^[0-9A-Za-z]+$")]
SemanticVersion = Annotated[str, StringConstraints(pattern=r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")]
MinecraftVersion = Annotated[str, StringConstraints(pattern=r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*))?$")]
FilePath = Annotated[Path, PathType('file')]
DirectoryPath = Annotated[Path, PathType('dir')]