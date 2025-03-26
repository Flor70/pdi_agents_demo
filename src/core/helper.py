# Add your utilities or helper functions to this file.

import os
from dotenv import load_dotenv, find_dotenv
from crewai import LLM


# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService                                                                                                                                     
def load_env():
    _ = load_dotenv(find_dotenv())

def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def get_groq_api_key():
    load_env()
    groq_api_key = os.getenv("GROQ_API_KEY")
    return groq_api_key

def get_cloud_api_key():
    load_env()
    cloud_api_key = os.getenv("CLOUD_API_KEY")
    return cloud_api_key


groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=get_groq_api_key(),
)

claude_llm = LLM(
    model="anthropic/claude-3-5-sonnet-latest",
    api_key=get_cloud_api_key(),
)