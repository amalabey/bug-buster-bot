from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from app.openai_feedback_provider import OpenAiFeedbackProvider
from app.openai_method_provider import OpenAiMethodProvider
from app.semantic_changeset_provider import SemanticChangesetProvider
from app.test_changeset_provider import TestChangesetProvider
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from app.models import Methods
from langchain.chains.openai_functions import (
    create_openai_fn_chain, create_structured_output_chain
)
from app.azure_devops.azure_repo_changeset_provider import AzureRepoPullRequestChangesetProvider

load_dotenv(".env")
load_dotenv(".env.local", override=True)

pr_change_provider = AzureRepoPullRequestChangesetProvider("amalzpd", "eShopOnWeb")
method_provider = OpenAiMethodProvider()
changeset_provider = SemanticChangesetProvider(pr_change_provider, method_provider)
changesets = changeset_provider.get_changesets("38")

feedback_provider = OpenAiFeedbackProvider()
for changeset in changesets:
    review_comments = feedback_provider.get_review_comments(changeset)
    print(review_comments)
