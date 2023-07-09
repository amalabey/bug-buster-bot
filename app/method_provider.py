from abc import ABC, abstractmethod
from app.models import Methods


class MethodProvider(ABC):
    @abstractmethod
    def get_methods(self, code_file_contents: str) -> Methods:
        pass
