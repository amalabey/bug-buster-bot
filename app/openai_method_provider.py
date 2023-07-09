from app.method_provider import MethodProvider
from app.models import Methods
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import create_structured_output_chain
from app.utils import add_line_numbers

MODEL_NAME = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.0


class OpenAiMethodProvider(MethodProvider):
    def get_methods(self, lang: str, code_file_contents: str) -> Methods:
        code_with_line_numbers = add_line_numbers(code_file_contents)
        prompt_msgs = [
            SystemMessage(
                content=f"You are a helpful assistant that understands {lang} programming language format and structure."
            ),
            HumanMessage(
                content="List method/function names in the following code with corresponding starting and end line numbers"
            ),
            HumanMessagePromptTemplate.from_template("{code}"),
            HumanMessage(content="Tips: Make sure to answer in the correct format"),
        ]
        prompt = ChatPromptTemplate(messages=prompt_msgs)
        llm = ChatOpenAI(model_name=MODEL_NAME,
                         temperature=DEFAULT_TEMPERATURE)

        chain = create_structured_output_chain(Methods, llm, prompt,
                                               verbose=True)
        result = chain.run(code=code_with_line_numbers)
        return Methods.parse_raw(result)
