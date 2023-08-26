from agent.agent import chat_with_agent
from utils.config import load_config, setup_environment_variables

# Load configuration from config.yml
config = load_config()

# Set up the environment variables
setup_environment_variables(config)

def main():
    print("Greetings! My name is", config["chatbot"]["name"], ". Type 'exit' to end the session.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = chat_with_agent(user_input, config["chatbot"]["name"])
        print(config["chatbot"]["name"] + ":", response)

if __name__ == "__main__":
    main()