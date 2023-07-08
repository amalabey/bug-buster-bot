from app.changeset_provider import ChangesetProvider
from difflib import ndiff


class TestChangesetProvider(ChangesetProvider):
    def get_changesets(self, pull_request_id: str):
        from_file_path = "test-data/CarParkService-v1.cs"
        to_file_path = "test-data/CarParkService-v2.cs"
        with open(from_file_path, 'r') as from_file:
            from_file_contents = from_file.read()
        with open(to_file_path, 'r') as to_file:
            to_file_contents = to_file.read()
        diff_lines = ndiff(from_file_contents.splitlines(keepends=True),
                           to_file_contents.splitlines(keepends=True))
        changesets = {}
        # changesets[to_file_path] = "".join(diff_lines)
        changesets[to_file_path] = to_file_contents
        return changesets
