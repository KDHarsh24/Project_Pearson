from langchain_core.messages import HumanMessage, SystemMessage
from model.watsonx import get_chatwatsonx


def get_initial_messages():
    return [
        SystemMessage(content="You are a helpful assistant.")
    ]


def main():
    chat = get_chatwatsonx()
    messages = get_initial_messages()
    print("Type 'exit' to end the chat.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            print("Chat ended.")
            break
        messages.append(HumanMessage(content=user_input))
        response = chat.invoke(messages)
        print("Assistant:", response.content)
        messages.append(response)

if __name__ == "__main__":
    main()
