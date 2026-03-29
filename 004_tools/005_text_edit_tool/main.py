from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file if present
client = Anthropic()
model = "claude-sonnet-4-5"


def chat_with_claude(user_message):
    """Simple chat function with Claude"""
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


if __name__ == "__main__":
    # Example usage
    result = chat_with_claude("What is Python used for?")
    print(result)
