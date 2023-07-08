from dotenv import load_dotenv
# from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from app.test_changeset_provider import TestChangesetProvider
from langchain.prompts import PromptTemplate


load_dotenv(".env")
load_dotenv(".env.local", override=True)

changeset_provider = TestChangesetProvider()
changesets = changeset_provider.get_changesets(None)
file, diff = list(changesets.items())[0]

prompt = PromptTemplate(
    input_variables=['lang', 'code'],
    template='''
    You are a senior {lang} Developer and a seasoned professional responsible 
    for evaluating and providing feedback on code written by other developers. 
    You possess deep knowledge of {lang} and its best practices, design patterns, 
    and software development principles. You also have extensive experience 
    in writing secure code. I would like you to review code written by 
    junior developer to ensure it is secure, performant, maintainable 
    and follows {lang} best practices.
    {code}
    ''')

# llm = OpenAI(temperature=0.0)
llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.0)

chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
result = chain.run(lang='C#', code=diff)
print(result)