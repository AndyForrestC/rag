import logging
import os
import pymilvus

from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex
)
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore

load_dotenv()

def get_streaming_query_engine():
    """
    Get a query engine specifically configured for streaming responses
    """
    model = os.getenv("MODEL", "gpt-4o")
    # Enable streaming at the LLM level
    llm = OpenAI(model=model, streaming=True)

    try:
        milvus_uri = os.getenv("MILVUS_URI")
        milvus_api_key = os.getenv("MILVUS_API_KEY")
        milvus_collection = os.getenv("MILVUS_COLLECTION")
        milvus_dim = os.getenv("MILVUS_DIMENSION")

        if not all([milvus_uri, milvus_api_key, milvus_collection]):
            raise ValueError("Missing required environment variables.")
    
        # load the existing collection
        vector_store = MilvusVectorStore(
            uri=milvus_uri,
            token=milvus_api_key,
            collection_name=milvus_collection,
            dim=milvus_dim,
            overwrite=False,
        )

        index = VectorStoreIndex.from_vector_store(vector_store)

        # Create streaming query engine without post-processors that might break streaming
        query_engine = index.as_query_engine(
            similarity_top_k=5,  # Get more docs since we don't use reranker for streaming
            llm=llm,
            streaming=True,
        )

    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid environment variables: {e}")
    except ConnectionError as e:
        raise ConnectionError(f"Failed to connect to Milvus: {e}")

    return query_engine
