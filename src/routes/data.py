from fastapi import FastAPI, APIRouter, Depends, UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController,ProcessController
from models import ResponseMassages as rs
import aiofiles
import os
import logging
from .schemes.data import ProcessRequest

logger = logging.getLogger("uvicorn.error")


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]

)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                     app_settings: Settings = Depends(get_settings)):
    # validate the inputs
    data_controller = DataController()
    is_valid,massage = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        
        if massage == rs.FILE_TYPE_NOT_SUPPORTED.value:
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={
                    "Massage":massage
                }
            )
    
        if massage == rs.FILE_SIZE_EXCEEDED.value:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "Massage":massage
                }
            )
        
    # save the files
    project_file_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_name(
        original_file_name = file.filename,
        project_id=project_id
    )


    try:
        async with aiofiles.open(file_path,"wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
             logger.error(f"Error while uploading file: {e}")
             return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "Massage":rs.FILE_UPLOAD_FAILED
                }
            )       

    return JSONResponse(
                content={
                    "Massage":massage,
                    "file_id" : file_id
                }
            )    


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    
    process_controller = ProcessController(project_id=project_id)
    
    file_content = process_controller.get_file_content(file_id=file_id)
    
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlab_size=overlap_size
    )
    
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={
                "Massage":rs.FILE_PROCESSING_FAILED.value
            }
        )
        
    return file_chunks 
    
