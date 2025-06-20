from pydantic import BaseModel, ConfigDict


class MCLBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, serialize_by_alias=True)
