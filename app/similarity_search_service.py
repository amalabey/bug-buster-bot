from abc import ABC, abstractmethod
from typing import List
from langchain.schema import Document


class SimilaritySearchService(ABC):
    @abstractmethod
    def find_similar(self, query: str) -> List[Document]:
        pass

    @abstractmethod
    def load(self, docs: List[Document]) -> List[Document]:
        pass