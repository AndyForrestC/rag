from typing import Optional
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.response.schema import StreamingResponse
from app.engine.index import get_streaming_query_engine

# Global variable to cache the streaming query engine
streaming_query_engine_cache = None

def init_streaming():
    global streaming_query_engine_cache  # Declare to use the global variable
    # Check if the streaming_query_engine is already initialized
    if streaming_query_engine_cache is not None:
        print('Using cached streaming query engine')
        return streaming_query_engine_cache

    streaming_query_engine_cache = get_streaming_query_engine()

    return streaming_query_engine_cache

def get_streaming_query_response(query_engine: BaseQueryEngine, query: str):
    """
    Function to get streaming response from query_engine.
    """
    return query_engine.query(query)
