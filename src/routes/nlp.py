from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models import ProjectModel, ChunkModel
from controllers import NLPController
from models import ResponseMassages as rs

import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp_router"]

)

@nlp_router.post("/index/push/{project_id}")
async def index__project_push(request: Request, project_id: str, push_request: PushRequest):
    # to create a project in the db
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )
    
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": rs.PROJECT_NOT_FOUND.value}
            )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    
    has_records = True
    page_no = 1
    inserted_chunks_count = 0
    
    while has_records:
        
        page_chunks = await chunk_model.get_chunks_by_project_id(
            project_id=project.id,
            page_no=page_no
            )
        
        
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
    
        # call nlp controller to process the chunks
        is_inserted = nlp_controller.index_into_vectordb(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset
        )
        
        

        if not is_inserted:
            return JSONResponse(
                status_code=status.status.HTTP_404_NOT_FOUND,
                content={
                    "signal": rs.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
            
        inserted_chunks_count += len(page_chunks)
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": rs.INSERT_INTO_VECTORDB_SUCCESS.value,
            "insertd_chunks_count" : inserted_chunks_count
        }
    )
    
@nlp_router.get('/index/info/{project_id}')
async def index_project_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": rs.PROJECT_NOT_FOUND.value}
            )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    
    collection_name = nlp_controller.create_collection_name(
        project_id=project_id
    )
    
    if not request.app.vector_db_client.is_collection_exists(collection_name):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": rs.VECTORDB_COLLECTION_NOT_EXISTS.value}
            )
        
    
    collection_info = nlp_controller.get_vectordb_collection_info(
        project=project
    )
    
    if collection_info:
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": rs.GET_VECTORDB_INFO_SUCCESS.value,
                "collection_info" : collection_info
            }
        )
    
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": rs.GET_VECTORDB_INFO_failed.value,
              
            }
        )
        

@nlp_router.post("/index/search/{project_id}")
async def index_project_search(request: Request, project_id: str,search_request : SearchRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": rs.PROJECT_NOT_FOUND.value}
            )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    
    results = nlp_controller.search_by_query_in_collection_vectordb(
        project=project,
        query=search_request.query,
        top_k=search_request.limit
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": rs.SEARCH_IN_VECTORDB_SUCCESS.value,
            "results" : results
        }
    )
    
        
    
    
    


        