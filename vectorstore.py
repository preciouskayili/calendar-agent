import os
import uuid
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Set index name and dimension for OpenAI embeddings
index_name = "chat-memory"
EMBEDDING_DIMENSION = 1536  # OpenAI text-embedding-ada-002 dimension

pc = Pinecone(os.getenv("PINECONE_API_KEY"))


def create_store():
    """Create the Pinecone index if it doesn't exist."""
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )


def get_embedding(text):
    """Get embedding for text using OpenAI's API."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return response.data[0].embedding


def upsert_message(session_id, role, content):
    """Store a message in Pinecone with its embedding and metadata."""
    embedding = get_embedding(content)
    message_id = str(uuid.uuid4())
    pc.Index(index_name).upsert(
        [
            {
                "id": message_id,
                "values": embedding,
                "metadata": {
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": time.time(),
                },
            }
        ]
    )


def fetch_session_messages(session_id, limit=100):
    """Retrieve all messages for a given session, ordered by timestamp."""
    results = pc.Index(index_name).query(
        vector=[0.0] * EMBEDDING_DIMENSION,  # dummy vector, we only want metadata
        filter={"session_id": {"$eq": session_id}},
        top_k=limit,
        include_metadata=True,
    )
    # Sort by timestamp
    messages = sorted(
        [r["metadata"] for r in results["matches"]], key=lambda x: x["timestamp"]
    )
    return messages


def get_new_session_id():
    """Generate a new unique session ID."""
    return str(uuid.uuid4())
