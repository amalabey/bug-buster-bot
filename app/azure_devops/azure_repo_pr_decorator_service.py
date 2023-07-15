import json
from typing import List
from app.azure_devops.azure_devops_client import AzureDevOpsClient
from app.models import ReviewComment
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

    def _get_existing_comments(self, api_client: AzureDevOpsClient, pr_id: str, target_file: str, start_line: int,
                               end_line: int) -> List[str]:
        existing_comments = list()
        api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullRequests/{pr_id}/threads?api-version=7.0"
        response = api_client.send_api_request(api_url, "GET")
        for thread in response["value"]:
            if "threadContext" not in thread or thread["threadContext"] is None:
                continue
            file_path = thread["threadContext"]["filePath"] if "filePath" in thread["threadContext"] else None
            line = thread["threadContext"]["rightFileStart"]["line"] if "rightFileStart" in thread["threadContext"] else 0

            if (file_path == target_file
               and line >= start_line
               and line <= end_line):
                for comment in thread["comments"]:
                    content = comment["content"] if "content" in comment else None
                    if content is not None:
                        existing_comments.append(content)
        return existing_comments

    def annotate(self, pr_id: str, file_path: str, start_line: int, end_line: int,
                 comments: List[ReviewComment]):
        api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullRequests/{pr_id}/threads?api-version=6.1-preview.1"
        api = AzureDevOpsClient()
        existing_comments = self._get_existing_comments(api, pr_id, file_path, start_line, end_line)
        for comment in comments:
            if (any(c for c in existing_comments if comment.feedback in c)):
                print(f"Comment already exists: {comment.feedback}")
                continue
            payload = self._get_comment_payload(file_path, start_line, comment)
            api.send_api_request(api_url, "POST", data=payload)
