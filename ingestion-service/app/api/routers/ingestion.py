from fastapi import APIRouter, HTTPException, UploadFile, File
from app.engine.generate import generate_datasource

ingestion_router = r = APIRouter()

@r.post("/upload")
def ingestion(file: UploadFile = File(...)):
    """Upload and process a file for ingestion into the vector database"""
    try:
        # TODO: Process the uploaded file
        generate_datasource()
        return {"message": "File processed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
