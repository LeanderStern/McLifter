from pydantic import BaseModel


class MCLBaseModel(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
        "strict": True,
    }
