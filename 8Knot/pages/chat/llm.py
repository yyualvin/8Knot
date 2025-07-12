"""
Simple LangChain functions to call OpenAI models.
"""
import os
from openai import OpenAI



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


def call_openai_stream(message, container=None):
    """
    Call OpenAI with streaming and update an external container.
    
    Args:
        message: Your message as a string
        container: External container to update (like a list or dict)
        
    Returns:
        The complete AI response as a string
    """
    # Create OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Make the streaming API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        stream=True
    )
    
    full_response = ""
    
    # Process each chunk
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            chunk_text = chunk.choices[0].delta.content
            full_response += chunk_text
            
            # Update external container if provided
            if container is not None:
                if isinstance(container, list):
                    container.append(chunk_text)
                elif isinstance(container, dict) and 'text' in container:
                    container['text'] += chunk_text
    
    return full_response


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Regular call
    result = call_openai("Hello, how are you?")
    print("Regular:", result)
    
    # Streaming with list container
    stream_container = []
    result = call_openai_stream("Tell me a short story", stream_container)
    print("Streamed chunks:", stream_container)
    print("Final result:", result)
    
    # Streaming with dict container
    dict_container = {'text': ''}
    result = call_openai_stream("What is Python?", dict_container)
    print("Dict container:", dict_container['text'])

