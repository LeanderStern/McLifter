from pydantic import Field, AnyHttpUrl

from base_model import MCLBaseModel
from constraints import JarFile


class FileResponse(MCLBaseModel):
    hash_algorithm: str | None = None
    hash: str | None = None
    url: AnyHttpUrl = Field(strict=False)
    filename: JarFile = Field(strict=False)