from typing import Tuple
from app.changeset_provider import ChangesetProvider
from app.models import ChangeSet
from app.azure_devops.azure_devops_client import AzureDevOpsClient


class AzureRepoPullRequestChangesetProvider(ChangesetProvider):
    def __init__(self, org: str, project_name: str, repo_name=None) -> None:
        super().__init__()
        self.org = org
        self.project_name = project_name
        self.repo_name = repo_name if repo_name is not None else project_name

    def _get_pr_branches(self, api_client: AzureDevOpsClient, pr_id: str) -> Tuple[str, str]:
        pr_api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullrequests/{pr_id}?api-version=6.1-preview.1"
        pr_response = api_client.send_api_request(pr_api_url, "GET")
        sourceBranchName = pr_response["sourceRefName"].replace("refs/heads/", "")
        targetBranchName = pr_response["targetRefName"].replace("refs/heads/", "")
        return (sourceBranchName, targetBranchName)

    def _get_pr_diff(self, api_client: AzureDevOpsClient, source: str, target: str):
        diff_api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/diffs/commits?baseVersion={target}&targetVersion={source}&api-version=7.1-preview.1"
        diff_response = api_client.send_api_request(diff_api_url, "GET")
        for change in diff_response["changes"]:
            if change["item"]["gitObjectType"] == "blob" and change["changeType"] in ("add", "edit"):
                file_path = change["item"]["path"]
                file_url = change["item"]["url"]
                is_new = True if change["changeType"] == "add" else False
                yield (file_path, file_url, is_new)

    def get_changesets(self, pull_request_id: str) -> list[ChangeSet]:
        api_client = AzureDevOpsClient()
        source, target = self._get_pr_branches(api_client, pull_request_id)
        changesets = list()
        for file_path, file_url, is_new in self._get_pr_diff(api_client,
                                                             source, target):
            file_contents = api_client.send_api_request(file_url, "GET",
                                                        raw_data=True)
            if not is_new:
                target_file_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/items?path={file_path}&versionDescriptor.version={target}&api-version=6.0"
                target_file_contents = api_client.send_api_request(
                    target_file_url, "GET", raw_data=True)
                changed_line_nums = self.get_changed_lines(
                    target_file_contents, file_contents)
            else:
                changed_line_nums = list()
            changeset = ChangeSet(path=file_path, contents=file_contents,
                                  changed_line_nums=changed_line_nums,
                                  is_new_file=is_new)
            changesets.append(changeset)
        return changesets
