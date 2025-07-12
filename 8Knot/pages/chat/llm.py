"""
Simple LangChain functions to call OpenAI models.
"""

from langchain_openai import ChatOpenAI
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


def call_openai(message):
    """
    Call OpenAI with a message and get a response.
    
    Args:
        message: Your message as a string
        
    Returns:
        The AI's response as a string
    """
    # Create OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": message}],
        temperature=0.7
    )
    
    return response.choices[0].message.content


# Example usage
if __name__ == "__main__":
    result = call_openai("Hello, how are you?")
    print(result)

