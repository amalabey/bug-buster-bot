from typing import Tuple
from app.feedback_provider import FeedbackProvider
from app.models import MethodInfo, ReviewComment, ReviewCommentCollection, SemanticChangeSet
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import create_structured_output_chain

MODEL_NAME = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.0


class OpenAiFeedbackProvider(FeedbackProvider):
    def _get_method_block(self, changeset: SemanticChangeSet, method: MethodInfo) -> str:
        code_lines = changeset.contents.splitlines(True)
        block_lines = code_lines[method.startLine - 1: method.endLine - 1]
        return "\n".join(block_lines)

    def get_review_comments(self, changeset: SemanticChangeSet) -> Tuple[MethodInfo, ReviewCommentCollection]:
        prompt_msgs = [
            SystemMessage(
                content=f"You are an experienced {changeset.lang} developer who can review code for correctness, security and best practices"
            ),
            HumanMessage(
                content=f"Review below code written by a junior developer in {changeset.lang}. List any feedback along with any suggested code changes where applicable"
            ),
            HumanMessagePromptTemplate.from_template("{code}"),
            HumanMessage(content="Tips: Make sure to answer in the correct format"),
        ]
        prompt = ChatPromptTemplate(messages=prompt_msgs)
        llm = ChatOpenAI(model_name=MODEL_NAME,
                         temperature=DEFAULT_TEMPERATURE)

        chain = create_structured_output_chain(ReviewCommentCollection, llm, prompt,
                                               verbose=True)
        feedback = list()
        for method in changeset.changed_methods:
            method_code = self._get_method_block(changeset, method)
            result = chain.run(code=method_code)
            comments = ReviewCommentCollection.parse_obj(result)
            feedback.append((method, comments))
        return feedback
