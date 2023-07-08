from abc import ABC, abstractmethod


class ChangesetProvider(ABC):
    @abstractmethod
    def get_changesets(self, pull_request_id: str):
        pass
