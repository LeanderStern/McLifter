from base_model import MCLBaseModel


class ModrinthHashResponse(MCLBaseModel):
    sha1: str
    sha512: str
