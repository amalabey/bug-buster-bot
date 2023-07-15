from typing import List
from app.similarity_search_service import SimilaritySearchService
from langchain.schema import Document
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma


class ChromaDbSimiliaritySearchService(SimilaritySearchService):
    def __init__(self) -> None:
        super().__init__()

    def load(self, docs: List[Document]):
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = Chroma.from_documents(docs, embedding_function)

    def find_similar(self, query: str) -> List[Document]:
        docs = self.db.similarity_search(query)
        return docs
