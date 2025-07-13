"""
A simple, direct script to chat with the Gemini API using the official
google-generativeai library.

This script takes user input from the terminal and prints the model's response.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai


def main():
    """
    Main function to configure the API, initialize the model, and start the chat loop.
    """
    # 1. --- API Configuration ---
    # Load environment variables from a .env file
    load_dotenv()

    # Get the API key from the environment
    api_key = os.getenv("GOOGLE_API_KEY")

    # Check if the API key is available. If not, exit with an error.
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.", file=sys.stderr)
        print("Please create a .env file and add your key: GOOGLE_API_KEY='Your-API-Key'", file=sys.stderr)
        sys.exit(1)

    # Configure the library with your API key. This is a one-time setup.
    try:
        genai.configure(api_key=api_key)
        print("✅ Google API configured successfully.")
    except Exception as e:
        print(f"Error configuring Google API: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. --- Model Initialization ---
    # Create an instance of the GenerativeModel.
    # You can easily swap the model name here if needed.
    # e.g., 'gemini-pro' for a balance of cost and performance.
    model_name = 'gemini-1.5-pro'
    try:
        model = genai.GenerativeModel(model_name)
        print(f"✅ Model '{model_name}' initialized. You can start chatting now.")
    except Exception as e:
        print(f"Error initializing model: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. --- Main Chat Loop ---
    print("\n--- Gemini Chat (Official API) ---")
    print("Type 'exit' or 'quit' to end the session.")

    while True:
        # Get user input from the terminal
        query = input("\nYou: ")

        # Check for exit condition
        if query.lower() in ["exit", "quit"]:
            print("Ending chat session. Goodbye!")
            break

        # Ensure the query is not empty
        if not query.strip():
            continue

        try:
            # Send the query to the model and get the response
            # The .generate_content() method is the core API call.
            response = model.generate_content(query)

            # Print the model's response text
            print(f"Gemini: {response.text}")

        except Exception as e:
            # Handle potential API errors gracefully (e.g., rate limits, invalid requests)
            print(f"\nAn error occurred: {e}", file=sys.stderr)
            print("Please check your API key, model access, and usage quotas.", file=sys.stderr)


# Run the main function when the script is executed
if __name__ == "__main__":
    main()