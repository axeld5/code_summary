import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

def generate_summary(text):
    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": f"""Summarize the following text from a code github repo:
                <text> {text} </text>
                Output the summary and only the summary.""",
            },
        ],
    )
    return chat_response.choices[0].message.content