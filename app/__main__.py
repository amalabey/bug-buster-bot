from dotenv import load_dotenv
from langchain.llms import OpenAI


load_dotenv(".env")
load_dotenv(".env.local", override=True)

llm = OpenAI(temperature=0.0)
response = llm.predict("What would be a good company name for a company that makes colorful socks?")
print(response)
