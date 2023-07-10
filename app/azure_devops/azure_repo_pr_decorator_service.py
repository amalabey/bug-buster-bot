import json
from app.azure_devops.azure_devops_client import AzureDevOpsClient
from app.models import ReviewCommentCollection
from app.pr_decorator_service import PullRequestDecoratorService


class AzureRepoPullRequestDecoratorService(PullRequestDecoratorService):
    def __init__(self, org: str,
                 project_name: str, repo_name=None) -> None:
        super().__init__()
        self.org = org
        self.project_name = project_name
        self.repo_name = repo_name if repo_name is not None else project_name

    def _get_comment_payload(self, file_path: str, line_num: int, comments: ReviewCommentCollection):
        comments_list = list()
        for comment in comments.comments:
            comment_text = f"{comment.feedback} \n ```\n{comment.example}\n```"
            comment_payload = {
                                    "parentCommentId": 0,
                                    "content": comment_text,
                                    "threadContext": {
                                        "filePath": file_path,
                                        "rightFileStartLine": line_num,
                                        "rightFileEndLine": line_num
                                    }
                                }
            comments_list.append(comment_payload)
        payload = json.dumps({
                        "comments": comments_list
                    })
        return payload

    def annotate(self, pr_id: str, file_path: str, line_num: int, comments: ReviewCommentCollection):
        api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullRequests/{pr_id}/threads?api-version=6.1-preview.1"
        payload = self._get_comment_payload(file_path, line_num, comments)
        api = AzureDevOpsClient()
        api.send_api_request(api_url, "POST", data=payload)
