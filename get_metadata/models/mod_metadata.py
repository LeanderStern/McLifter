from pydantic import BaseModel


class ModMetadata(BaseModel):
    id: str
    version: 
    depends: dict

    def __contains__(self, values) -> bool:
        for value in values:
            if self.id is value.id:
                return True
        return False