"""
This is a simple exercise to get you started with the API.
It will ask you to write a function that will call the chat API and return the response.
"""
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


# Make an initial list of messages to send to the API. This will be the conversation history that we will send to the API.
messages = []
client = Anthropic()
model = "claude-sonnet-4-0"

while True:
    # Get user input and add it to the messages list
    user_input = input("You: ")
    print(f"User input: {user_input}")

    messages.append({"role": "user", "content": user_input})
    
    resp = client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages
    )

    print(f"Assistant: {resp.content[0].text}")
    messages.append({"role": "assistant", "content": resp.content[0].text})

