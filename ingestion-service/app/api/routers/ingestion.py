from fastapi import APIRouter, HTTPException, UploadFile, File
from app.engine.generate import process_uploaded_file

ingestion_router = r = APIRouter()


@r.post("/upload")
def ingestion(file: UploadFile = File(...)):
    """Upload and process a file for ingestion into the vector database"""
    try:
        # Process the uploaded file
        result = process_uploaded_file(file)
        return {
            "message": "File processed successfully",
            "filename": result["filename"],
            "nodes_created": result["nodes_created"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
