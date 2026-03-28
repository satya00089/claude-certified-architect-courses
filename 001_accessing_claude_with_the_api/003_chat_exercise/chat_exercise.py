"""
This is a simple exercise to get you started with the API.
It will ask you to write a function that will call the chat API and return the response.
"""

from dotenv import load_dotenv


load_dotenv()


# Make an initial list of messages to send to the API. This will be the conversation history that we will send to the API.
messages = []

while True:
    # Get user input and add it to the messages list
    user_input = input("You: ")
    print(f"User input: {user_input}")

    # Call the chat API with the messages list and get the response

    # Call the chat API function here (you need to implement this function)
