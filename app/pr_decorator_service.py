from abc import ABC, abstractmethod
from typing import List
from app.models import ReviewComment


class PullRequestDecoratorService(ABC):
    @abstractmethod
    def annotate(self, pr_id: str, file_path: str, start_line: int, end_line: int, comments: List[ReviewComment]):
        pass
