from pydantic import Field, AnyHttpUrl

from base_model import MCLBaseModel
from constraints import JarFile


class FileResponse(MCLBaseModel):
    hashes: dict[str, str] = Field(description="The key is the hashing algorithm and the value is the string version of the hash.")
    url: AnyHttpUrl = Field(strict=False)
    filename: JarFile = Field(strict=False)