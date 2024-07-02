import asyncio
import sys
import subprocess
import re
import speech_recognition as sr
from ollama import AsyncClient

# Initialize the speech recognizer
recognizer = sr.Recognizer()

async def get_question_from_speech():
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Speak your question:")
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Speech Recognition
        question = recognizer.recognize_google(audio)
        return question
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

async def chat():
    """
    Stream a chat from Llama using the AsyncClient.
    """
    # Check if the user provided a custom question via command-line arguments
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        # Get question from speech
        question = await get_question_from_speech()

    if not question:
        print("No question provided. Please provide your question.")
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
