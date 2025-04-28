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
            model="gpt-4o",  # or "gpt-4-turbo", etc
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
