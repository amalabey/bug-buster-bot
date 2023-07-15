import json
from typing import List
from app.azure_devops.azure_devops_client import AzureDevOpsClient
from app.models import ReviewComment, ReviewCommentCollection
from app.pr_decorator_service import PullRequestDecoratorService


class AzureRepoPullRequestDecoratorService(PullRequestDecoratorService):
    def __init__(self, org: str,
                 project_name: str, repo_name=None) -> None:
        super().__init__()
        self.org = org
        self.project_name = project_name
        self.repo_name = repo_name if repo_name is not None else project_name

    def _get_comment_payload(self, file_path: str, line_num: int, comment: ReviewComment):
        comment_text = f"{comment.feedback} \n ```\n{comment.example}\n```"
        payload = json.dumps({
                        "comments": [
                            {
                                "parentCommentId": 0,
                                "content": comment_text,
                                "commentType": 1
                            }
                        ],
                        "status": 1,
                        "threadContext": {
                            "filePath": file_path,
                            "leftFileEnd": None,
                            "leftFileStart": None,
                            "rightFileEnd": {
                                "line": line_num,
                                "offset": 1
                            },
                            "rightFileStart": {
                                "line": line_num,
                                "offset": 1
                            }
                        },
                        "pullRequestThreadContext": {
                            "changeTrackingId": 0
                        }
                    })
        return payload

    def annotate(self, pr_id: str, file_path: str, line_num: int,
                 comments: List[ReviewComment]):
        api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullRequests/{pr_id}/threads?api-version=6.1-preview.1"
        api = AzureDevOpsClient()
        for comment in comments:
            payload = self._get_comment_payload(file_path, line_num, comment)
            api.send_api_request(api_url, "POST", data=payload)
