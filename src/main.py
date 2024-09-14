from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # code here will run before starting
    
    # Making the connection
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    
    # for testing
    print(app.mongo_conn)
    
    # setting LLMs
    llm_provider_factory =  LLMProviderFactory(config=settings)
    # generative
    app.generation_client = llm_provider_factory.create(config=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)
    
    # embedding
    app.embedding_client = llm_provider_factory.create(config=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID,
                                             embedding_size = settings.EMBEDDING_MODEL_SIZE)
    

    yield
    
    # code here will run after shutdown
    # closing the connection
    app.mongo_conn.close()
    

app = FastAPI(lifespan = lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
