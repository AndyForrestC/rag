import logging
import os
import tempfile
from io import StringIO
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core.node_parser import SentenceWindowNodeParser
from fastapi import UploadFile

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

model = os.getenv("MODEL", "gpt-3.5-turbo")
llm = OpenAI(model=model)
embed_model = OpenAIEmbedding(model="text-embedding-ada-002")


def generate_datasource():
    try:
        milvus_uri = os.getenv("MILVUS_URI")
        milvus_api_key = os.getenv("MILVUS_API_KEY")
        milvus_collection = os.getenv("MILVUS_COLLECTION")
        milvus_dimension = int(os.getenv("MILVUS_DIMENSION", "1536"))  # Default to 1536

        if not all([milvus_uri, milvus_api_key, milvus_collection]):
            raise ValueError(
                "Missing required environment variables: "
                "MILVUS_URI, MILVUS_API_KEY, or MILVUS_COLLECTION."
            )

        # Create MilvusVectorStore
        vector_store = MilvusVectorStore(
            uri=milvus_uri,
            token=milvus_api_key,
            collection_name=milvus_collection,
            dim=milvus_dimension,  # mandatory for new collection creation
            overwrite=True,
        )

        # Create StorageContext
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # create the sentence window node parser
        node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )

        documents = SimpleDirectoryReader("data").load_data()
        nodes = node_parser.get_nodes_from_documents(documents)
        VectorStoreIndex(
            nodes, storage_context=storage_context, embed_model=embed_model
        )

    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid environment variables: {e}")
    except ConnectionError as e:
        raise ConnectionError(f"Failed to connect to Milvus: {e}")


def process_uploaded_file(file: UploadFile):
    """Process a single uploaded file and add it to the vector database"""
    try:
        milvus_uri = os.getenv("MILVUS_URI")
        milvus_api_key = os.getenv("MILVUS_API_KEY")
        milvus_collection = os.getenv("MILVUS_COLLECTION")
        milvus_dimension = int(os.getenv("MILVUS_DIMENSION", "1536"))

        if not all([milvus_uri, milvus_api_key, milvus_collection]):
            raise ValueError(
                "Missing required environment variables: "
                "MILVUS_URI, MILVUS_API_KEY, or MILVUS_COLLECTION."
            )

        # Validate file type and extension
        allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.csv'}
        allowed_content_types = {
            'text/plain', 'text/markdown', 'application/pdf',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/csv'
        }
        
        # Check file extension
        if file.filename:
            file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                raise ValueError(f"Unsupported file extension: {file_ext}. Allowed: {', '.join(allowed_extensions)}")
        
        # Check content type
        if file.content_type and file.content_type not in allowed_content_types:
            raise ValueError(f"Unsupported content type: {file.content_type}. Allowed: {', '.join(allowed_content_types)}")

        # Read file content
        content = file.file.read()
        
        # Check for binary content by looking for null bytes and other binary indicators
        if b'\x00' in content[:100]:  # Check first 100 bytes for null bytes
            raise ValueError("Binary content detected - only text files are supported")

        # Handle different file types
        if file.content_type and "text" in file.content_type:
            text_content = content.decode('utf-8')
        else:
            # For other file types, try to decode as text
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError(f"Unable to decode file as text: {file.content_type}")

        # Create Document object
        document = Document(
            text=text_content,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            }
        )

        # Create MilvusVectorStore
        vector_store = MilvusVectorStore(
            uri=milvus_uri,
            token=milvus_api_key,
            collection_name=milvus_collection,
            dim=milvus_dimension,
            overwrite=False,  # Don't overwrite existing data
        )

        # Create StorageContext
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create the sentence window node parser
        node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )

        # Process the document
        nodes = node_parser.get_nodes_from_documents([document])
        VectorStoreIndex(
            nodes, storage_context=storage_context, embed_model=embed_model
        )

        logger.info(f"Successfully processed file: {file.filename}")
        return {"status": "success", "filename": file.filename, "nodes_created": len(nodes)}

    except (KeyError, ValueError) as e:
        logger.error(f"Configuration error: {e}")
        raise ValueError(f"Invalid environment variables: {e}")
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise ConnectionError(f"Failed to connect to Milvus: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing file {file.filename}: {e}")
        raise Exception(f"Failed to process file: {e}")


if __name__ == "__main__":
    generate_datasource()
