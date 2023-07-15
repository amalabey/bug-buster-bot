from typing import List
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from app.azure_devops.azure_devops_client import AzureDevOpsClient


class AzureRepoPullRequestCommentLoader(BaseLoader):
    def __init__(self, org: str,
                 project_name: str, pr_id: str, repo_name=None) -> None:
        super().__init__()
        self.org = org
        self.project_name = project_name
        self.repo_name = repo_name if repo_name is not None else project_name
        self.pr_id = pr_id

    def load(self) -> List[Document]:
        docs = list()
        api_client = AzureDevOpsClient()
        api_url = f"https://dev.azure.com/{self.org}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullRequests/{self.pr_id}/threads?api-version=7.0"
        response = api_client.send_api_request(api_url, "GET")
        for thread in response["value"]:
            if "threadContext" not in thread or thread["threadContext"] is None:
                continue
            file_path = thread["threadContext"]["filePath"] if "filePath" in thread["threadContext"] else None
            line = thread["threadContext"]["rightFileStart"]["line"] if "rightFileStart" in thread["threadContext"] else 0

            if file_path is not None and line > 0:
                for comment in thread["comments"]:
                    content = comment["content"] if "content" in comment else None
                    if content is not None:
                        docs.append(Document(page_content=content, metadata={"file_path": file_path, "line": line}))
        return docs
