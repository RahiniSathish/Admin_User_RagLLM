import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = AzureChatOpenAI(
    api_key=os.getenv("API_KEY"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_version=os.getenv("API_VERSION"),
    deployment_name=os.getenv("DEPLOYMENT_ID"),
    openai_api_type="azure",
    temperature=0
)
def get_response(prompt):
    return llm.invoke(prompt)
