from fastapi import FastAPI, APIRouter, Depends, UploadFile,status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController,ProcessController
from models import ResponseMassages as rs
import aiofiles
import os
import logging
from .schemes.data import ProcessRequest
from models import ChunkModel, ProjectModel, AssetModel
from models.db_schemes import DataChunk, Asset
from models.enum.AssetEnum import AssetTypeEnum


logger = logging.getLogger("uvicorn.error")


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]

)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request,project_id: str, file: UploadFile,
                     app_settings: Settings = Depends(get_settings)):
    
    # to create a project in the db
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    
    # validate the inputs
    data_controller = DataController()
    is_valid, massage = data_controller.validate_uploaded_file(file=file)

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
    file_path, file_name = data_controller.generate_unique_name(
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
             
             
    # write the file into the db
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
        )

    asset_resource = Asset(
        asset_project_id = project.id,
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_name,
        asset_size = os.path.getsize(file_path)
        
    )
    
    asset_record = await asset_model.create_asset(asset=asset_resource)
        

    return JSONResponse(
                content={
                    "Massage":massage,
                    "file_id" : str(asset_record.id),
                    "file_name" : str(asset_record.asset_name)
                }
            )    


@data_router.post("/process/{project_id}")  # process for all files or one file
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    asset_name = process_request.asset_name
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )
        

    # get files ids or only one file id
    project_assets = await asset_model.get_assets(
        asset_name=asset_name,
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value
    )

    logger.info(f"the value of get assets return = {asset_name}")
    # if nothing in list
    if project_assets is None :
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "signal": rs.FILE__NAME_INCORRECT.value

            }
        )    
    
    

    # iterate over files to get ids
    project_assets_ids = {
        record.id:record.asset_name
        for record in project_assets
    }
    
    # if nothing in list
    if len(project_assets_ids) == 0 :
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "signal": rs.FILE_NO_FILES_ERROR.value 

            }
        )    
    
        
        
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
         )
        
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )
        
        
        
    process_controller = ProcessController(project_id=project_id)
    no_chunks = 0
    no_files = 0
    for asset_id,file_name in project_assets_ids.items():
        file_content = process_controller.get_file_content(file_name=file_name)
        
        if file_content is None:
            logger.error(f"error while processing file {file_name}")
            continue
        
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_name=file_name,
            chunk_size=chunk_size,
            overlab_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": rs.FILE_PROCESSING_FAILED.value
                }
            )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id = asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

    
        no_chunks += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    return JSONResponse(
        content={
            "signal": rs.FILE_PROCESSING_SUCCESS.value,
            "inserted_chunks": no_chunks,
            "processed_files": no_files
        }
    )
    
