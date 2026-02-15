from analyst_agent_chat.controller.chat_controller import ChatController

def main():
    chat = ChatController()

    print("🤖 Multi-Agent Chatbot")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        response = chat.handle_message(user_input)
        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()