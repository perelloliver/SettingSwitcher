from typing import Any, Dict, List, Optional, Tuple
from langchain.embeddings import OpenAIEmbeddings
import math
import faiss
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.experimental.generative_agents import (
    GenerativeAgent,
    GenerativeAgentMemory,
)

from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings

def relevance_score_fn(score:float) -> float:
  ##Return a similarity score scaled between 0,1
  ##Differs depending on the distance/similarity metric of VectorStore
  ##And embedding scale (OpenAI are unit norm)
  ##0 is most similar, sqrt(2) most dissimilar

  #From Langchain
  return 1.0 - score / math.sqrt(2)

def create_new_memory_retriever():
  #From Langchain
  #Creates a new vector store retriever unique to the agent
  #Define embedding model
  embeddings_model = OpenAIEmbeddings()
  #Initialize empty vectorstore
  embedding_size = 1536
  index = faiss.IndexFlatL2(embedding_size)
  vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {}, relevance_score_fn=relevance_score_fn)
  return TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, other_score_keys=["importance"], k=15)
