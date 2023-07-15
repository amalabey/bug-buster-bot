from typing import List
from app.similarity_search_service import SimilaritySearchService
from app.models import ReviewComment


class CommentFilterService():
    def __init__(self, search_svc: SimilaritySearchService) -> None:
        super().__init__()
        self.search_svc = search_svc

    def get_filtered_comments(self, comments: List[ReviewComment], file_path: str,
                              start_line: int, end_line: int) -> List[ReviewComment]:
        filtered_list = list()
        for comment in comments:
            similar_comments = self.search_svc.find_similar(comment.feedback)
            if similar_comments and len(similar_comments) > 0:
                if next((c for c in similar_comments if c.metadata["file_path"] == file_path
                         and c.metadata["line"] >= start_line
                         and c.metadata["line"] <= end_line), None):
                    continue
            filtered_list.append(comment)
        return filtered_list
