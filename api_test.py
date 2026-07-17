import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

try:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Hello"
    )
    print(response.output_text)
except Exception as e:
    print(e)