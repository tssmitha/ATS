import os
from fastapi import HTTPException, UploadFile

#configuration
max_file_size = 10 * 1024 * 1024 #10MB
allowed_extensions = {'.pdf' , '.doc' , '.txt'}

def validate_file(file: UploadFile) -> None:
        # Checking extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Checking file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {max_file_size / 1024 / 1024}MB"
            )