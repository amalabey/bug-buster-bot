from abc import ABC, abstractmethod
from app.models import ReviewComment, ReviewCommentCollection


class PullRequestDecoratorService(ABC):
    @abstractmethod
    def annotate(self, pr_id: str, file_path: str, line_num: int, comments: ReviewCommentCollection):
        pass
