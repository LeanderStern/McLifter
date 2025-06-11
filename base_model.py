from pydantic import BaseModel


class MMUBaseModel(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
        "strict": True,
    }
