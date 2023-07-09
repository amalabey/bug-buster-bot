from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
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

test = AzureRepoPullRequestChangesetProvider("amalzpd", "eShopOnWeb")
res = test.get_changesets("38")

# changeset_provider = TestChangesetProvider()
# changesets = changeset_provider.get_changesets(None)
# file, diff = list(changesets.items())[0]

# prompt_msgs = [
#         SystemMessage(
#             content='You are a helpful assistant that understands C# programming language format and structure.'
#         ),
#         HumanMessage(content="List method/function names in the following code with corresponding starting and end line numbers"),
#         HumanMessagePromptTemplate.from_template("{code}"),
#         HumanMessage(content="Tips: Make sure to answer in the correct format")
#     ]
# prompt = ChatPromptTemplate(messages=prompt_msgs)

# llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.0)

# chain = create_structured_output_chain(Methods, llm, prompt, verbose=True)
# result = chain.run(lang='C#', code=diff)

# print(result)