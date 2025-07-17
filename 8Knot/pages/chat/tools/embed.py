from pinecone import Pinecone, ServerlessSpec
import os
import json
from openai import OpenAI



pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Get embeddings using the best Embedddings Model
def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding


def create_index(index_name, pc):
    """
    Create a Pinecone index if it doesn't exist and return the index object.
    
    Args:
        index_name (str): Name of the index to create
        pc (Pinecone): Pinecone client instance
    
    Returns:
        Index: Pinecone index object for performing operations
    """
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            )
        )
        print(f"Created new index: {index_name}")
    else:
        print(f"Index {index_name} already exists")
    
    # Return the index object for immediate use
    return pc.Index(index_name)

def upsert_function(index, tool_file: str):
    with open(tool_file, "r") as f:
        tools = json.load(f)
    
    for tool in tools:
        name = tool["name"]
        description = tool["description"]
        embedding = embed(f"{tool}")
        index.upsert(vectors=[{"id": name, "values": embedding, "metadata": {"tool_json": json.dumps(tool)}}])
        print(f"Upserted {name}")

def search_function(index, query, top_k=5):
    response = index.query(
        vector=embed(query),
        top_k=top_k,
        include_metadata=True
    )
    # Extract tool data from response
    tools = []
    for match in response.matches:
        tool_json = match.metadata["tool_json"]
        tools.append(json.loads(tool_json))
    return tools

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    index = create_index("8knot-index", pc)
    upsert_function(index, "8Knot/pages/chat/tools/tools.json")
    print(search_function(index, "show commits over time"))