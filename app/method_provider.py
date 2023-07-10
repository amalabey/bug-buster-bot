from abc import ABC, abstractmethod
from app.models import Methods


class MethodProvider(ABC):
    @abstractmethod
    def get_methods(self, lang: str, code_file_contents: str) -> Methods:
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
        methods = Methods.parse_obj(result)
        # Remove any false detection of entire class as a method
        # If a method contains other methods it's probably the class
        cleansed_methods = [m for m in methods.methods
                            if not any(n.startLine >= m.startLine
                                       and n.endLine <= m.endLine
                                       and n.name != m.name
                                       for n in methods.methods)]
        methods.methods = cleansed_methods
        return methods
