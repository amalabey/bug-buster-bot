from dotenv import load_dotenv
from app.azure_devops.azure_repo_pr_decorator_service import AzureRepoPullRequestDecoratorService
from app.openai_feedback_provider import OpenAiFeedbackProvider
from app.openai_method_provider import OpenAiMethodProvider
from app.semantic_changeset_provider import SemanticChangesetProvider
from app.azure_devops.azure_repo_changeset_provider import AzureRepoPullRequestChangesetProvider

load_dotenv(".env")
load_dotenv(".env.local", override=True)

az_org = "amalzpd"
az_project = "eShopOnWeb"
pr_id = "38"

pr_change_provider = AzureRepoPullRequestChangesetProvider(az_org, az_project)
method_provider = OpenAiMethodProvider()
changeset_provider = SemanticChangesetProvider(pr_change_provider, method_provider)
changesets = changeset_provider.get_changesets(pr_id)

feedback_provider = OpenAiFeedbackProvider()
pr_decorator = AzureRepoPullRequestDecoratorService(az_org, az_project)
for changeset in changesets:
    feedback_list = feedback_provider.get_review_comments(changeset)
    for method, comments in feedback_list:
        pr_decorator.annotate(pr_id, changeset.path, method.startLine, comments)

print("done.")
