import asyncio
import sys
from ollama import AsyncClient
import re
import subprocess

async def chat():
    """
    Stream a chat from Llama using the AsyncClient.
    """
    # Check if the user provided a custom question via command-line arguments
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print("Please provide your question in the following format:")
        print("python3 script_name.py -- Your question here")
        return  # Exit the function if no question is provided

    message = {
        "role": "user",
        "content": question
    }

    response = ""
    async for part in await AsyncClient().chat(
        model="llama3", messages=[message], stream=True
    ):
        response += part["message"]["content"]

    # Extract Linux commands wrapped in triple backticks
    commands = re.findall(r'```([^`]+)```', response, re.DOTALL)

    # Print each command with numbering
    for i, command in enumerate(commands, 1):
        print(f"{i}. {command.strip()}")  # Strip to remove extra whitespace

    # Prompt user to choose a command
    if commands:
        choice = input("Enter the number of the command you want to run: ")

        try:
            choice_index = int(choice) - 1
            selected_command = commands[choice_index].strip()

            # Run the selected command in the terminal
            print(f"Running command: {selected_command}")
            subprocess.run(selected_command, shell=True)
        
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")

asyncio.run(chat())
