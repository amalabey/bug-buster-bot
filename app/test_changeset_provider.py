from app.changeset_provider import ChangesetProvider
from app.models import ChangeSet


class TestChangesetProvider(ChangesetProvider):
    def get_changesets(self, pull_request_id: str) -> list[ChangeSet]:
        from_file_path = "test-data/CarParkService-v1.cs"
        to_file_path = "test-data/CarParkService.cs"
        with open(from_file_path, 'r') as from_file:
            from_file_contents = from_file.read()
        with open(to_file_path, 'r') as to_file:
            to_file_contents = to_file.read()

        changesets = list()
        changed_line_nums = self.get_changed_lines(from_file_contents,
                                                   to_file_contents)
        changesets.append(ChangeSet(to_file_path, to_file_contents,
                                    changed_line_nums, False))
        return changesets
