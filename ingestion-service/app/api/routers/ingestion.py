from fastapi import APIRouter, UploadFile, File, HTTPException
from app.engine.generate import generate_datasource, process_uploaded_file
import os
import tempfile

ingestion_router = r = APIRouter()

@r.post("")
def ingestion():
    generate_datasource()

@r.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file for ingestion"""
    try:
        # Validate file type
        allowed_extensions = {".pdf", ".doc", ".docx", ".txt"}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the file
        result = await process_uploaded_file(temp_file_path, file.filename)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return {
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "result": result
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
