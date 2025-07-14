import os
from openai import OpenAI
import json

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

def call_tools(message, tools):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=[{"role": "user", "content": f"You are a helpful assistant. You are given a message and a list of graphs tools. Call the tools that you think would help the user answer the question. The message is: {message}"}],
        tools=tools,
    )

    return response.output

def code_languages_graph(view="files"):
    return f"Code languages graph for {view}"

if __name__ == "__main__":
    tools = json.load(open("8Knot/pages/chat/tools/tools.json"))
    # Use a chat interface to call the tool
    while True:
        message = input("Enter a message: ")
        response = call_tools(message, tools)

        for tool in response:
            args = getattr(tool, 'arguments', {})
            name = getattr(tool, 'name', None)

            print(args)
            print(name)
            
            if isinstance(args, str):
                args = json.loads(args)
            
            if name:
                print(globals()[name](**args))
            
