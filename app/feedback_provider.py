from abc import ABC, abstractmethod
from app.models import ReviewCommentCollection, SemanticChangeSet


class FeedbackProvider(ABC):
    @abstractmethod
    def get_review_comments(self, changeset: SemanticChangeSet) -> ReviewCommentCollection:
        pass
