from difflib import Differ
from typing import Iterator
from app.changeset_provider import ChangesetProvider
from app.method_provider import MethodProvider
from app.models import MethodInfo, SemanticChangeSet
from app.utils import detect_lang


class SemanticChangesetProvider:
    def __init__(self, changeset_provider: ChangesetProvider,
                 method_provider: MethodProvider) -> None:
        self.changeset_provider = changeset_provider
        self.method_provider = method_provider

    def _get_changed_lines(self, source: str, target: str) -> Iterator[int]:
        differ = Differ()
        diffs = differ.compare(source.splitlines(True), target.splitlines(True))
        lineNum = 0
        for line in diffs:
            code = line[:2]
            if code in ("  ", "+ "):
                lineNum += 1
            if code == "+ ":
                yield lineNum

    def _get_changed_blocks(self, source: str, target: str) -> Iterator[tuple[int, int]]:
        index = 0
        blockStart = 0
        for changed_line_num in self._get_changed_lines(source, target):
            index += 1
            if blockStart == 0:
                blockStart = changed_line_num
                continue
            elif changed_line_num > index:
                yield (blockStart, changed_line_num)
                blockStart = 0
            index = changed_line_num
        if blockStart > 0:
            yield (blockStart, index)

    def _get_changed_methods(self, source: str, target: str, methods: list[MethodInfo]) -> list[MethodInfo]:
        changed_methods = set()
        for start, end in self._get_changed_blocks(source, target):
            matched_methods = [m for m in methods if m.endLine >= start and m.startLine <= end]
            changed_methods = changed_methods | set(matched_methods)
        return list(changed_methods)

    def get_changesets(self, pull_request_id: str) -> list[SemanticChangeSet]:
        semantic_changesets = list()
        changesets = self.changeset_provider.get_changesets(pull_request_id)
        for changeset in changesets:
            lang = detect_lang(changeset.path)
            methods = self.method_provider.get_methods(lang, changeset.contents).methods
            if changeset.is_new_file:
                semantic_changesets.append(
                    SemanticChangeSet.from_changeset(changeset, methods))
            else:
                changed_methods = self._get_changed_methods(
                    changeset.original_contents,
                    changeset.contents,
                    methods)
                semantic_changesets.append(
                    SemanticChangeSet.from_changeset(changeset, changed_methods))
        return semantic_changesets
