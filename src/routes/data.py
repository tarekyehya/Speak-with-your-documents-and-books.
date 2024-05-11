from fastapi import FastAPI, APIRouter, Depends, UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseMassages as rs
import aiofiles
import os


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]

)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                     app_settings: Settings = Depends(get_settings)):
    # validate the inputs
    is_valid,massage = DataController().validate_uploaded_file(file=file)

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
    file_path = os.path.join(
        project_file_path,
        file.filename
    )

    async with aiofiles.open(file_path,"wb") as f:
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)


    return JSONResponse(
                content={
                    "Massage":massage
                }
            )    





