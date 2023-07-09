from abc import ABC, abstractmethod
from difflib import Differ
from app.models import ChangeSet


class ChangesetProvider(ABC):
    @abstractmethod
    def get_changesets(self, pull_request_id: str) -> list[ChangeSet]:
        pass

    def get_changed_lines(self, source: str, target: str) -> list[str]:
        differ = Differ()
        changed_lines = list()
        diffs = differ.compare(source, target)
        lineNum = 0
        for line in diffs:
            code = line[:2]
            if code in ("  ", "+ "):
                lineNum += 1
            if code == "+ ":
                changed_lines.append(lineNum)
        return changed_lines
