from abc import ABC, abstractmethod
from typing import List

from get_metadata.models import ModMetadata


class GetMetadata(ABC):

    @property
    @abstractmethod
    def mods(self) -> List[ModMetadata]:
        pass