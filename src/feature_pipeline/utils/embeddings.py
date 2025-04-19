from typing import List

import numpy as np
from InstructorEmbedding import INSTRUCTOR
from openai import OpenAI

from src.feature_pipeline.config import settings

client = OpenAI()


def embedd_text(text: str):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text,
        model=settings.EMBEDDING_MODEL_ID,
    )
    # Extract the list of floats
    embedding_list: List[float] = response.data[0].embedding
    # Convert to NumPy array
    embedding_array: np.ndarray = np.array(embedding_list)
    return embedding_array


def embedd_repositories(text: str):
    model = INSTRUCTOR("hkunlp/instructor-xl")
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])
