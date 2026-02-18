from openai import OpenAI
import os
import numpy as np

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embeddings(query: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    return response.data[0].embedding

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))