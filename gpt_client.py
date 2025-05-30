from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4-turbo", etc
            messages=[
                {"role": "system", "content": "You are an expert ERPNext assistant and business consultant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error contacting OpenAI: {e}"


def ask_gpt_custom(system_message: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error contacting OpenAI: {e}"
