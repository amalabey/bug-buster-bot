import argparse
from dotenv import load_dotenv
from app.comment_filter_service import CommentFilterService
from app.azure_devops.azure_repo_pr_comment_loader import AzureRepoPullRequestCommentLoader
from app.azure_devops.azure_repo_pr_decorator_service import AzureRepoPullRequestDecoratorService
from app.chromadb_similartiy_search_service import ChromaDbSimiliaritySearchService
from app.openai.openai_feedback_provider import OpenAiFeedbackProvider
from app.openai.openai_method_provider import OpenAiMethodProvider
from app.semantic_changeset_provider import SemanticChangesetProvider
from app.azure_devops.azure_repo_changeset_provider import AzureRepoPullRequestChangesetProvider

# Create the argument parser
parser = argparse.ArgumentParser(description='Review code changes in a Pull Request using LLMs')

# Add arguments
parser.add_argument('-o', '--org', type=str, help='Name of the Azure DevOps organisation')
parser.add_argument('-p', '--project', type=str, help='Azure DevOps project name')
parser.add_argument('-i', '--id', type=str, help='Pull request id/number')

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the parsed arguments
az_org = args.org
az_project = args.project
pr_id = args.id

load_dotenv(".env")
load_dotenv(".env.local", override=True)

pr_change_provider = AzureRepoPullRequestChangesetProvider(az_org, az_project)
method_provider = OpenAiMethodProvider()
changeset_provider = SemanticChangesetProvider(pr_change_provider,
                                               method_provider)
changesets = changeset_provider.get_changesets(pr_id)

comment_loader = AzureRepoPullRequestCommentLoader(az_org, az_project, pr_id)
comment_docs = comment_loader.load()
similarity_search_svc = ChromaDbSimiliaritySearchService()
similarity_search_svc.load(comment_docs)
filter_svc = CommentFilterService(similarity_search_svc)

feedback_provider = OpenAiFeedbackProvider()
pr_decorator = AzureRepoPullRequestDecoratorService(az_org, az_project,
                                                    similarity_search_svc)
for changeset in changesets:
    feedback_list = feedback_provider.get_review_comments(changeset)
    for method, comments in feedback_list:
        filtered_comments = filter_svc.get_filtered_comments(comments.comments,
                                                             changeset.path,
                                                             method.startLine,
                                                             method.endLine)
        if len(filtered_comments) > 0:
            pr_decorator.annotate(pr_id, changeset.path, method.startLine,
                                  filtered_comments)
print("Done.")
