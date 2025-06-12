from base_model import MCLBaseModel
from constraints import Base62Str


class GetVersionResponse(MCLBaseModel):
    id: Base62Str