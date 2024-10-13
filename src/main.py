from fastapi import FastAPI
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProvidersFactory import VectorDBProvidersFactory
from stores.llm.templates.template_parser import TemplateParser

@asynccontextmanager
async def lifespan(app: FastAPI):
    # code here will run before starting
    
    # Making the connection
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    
    # setting instances
    llm_provider_factory =  LLMProviderFactory(config=settings)
    vecttor_db_provider_factory = VectorDBProvidersFactory(config=settings)
    
    # generative
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)
    
    # embedding
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID,
                                             embedding_size = settings.EMBEDDING_MODEL_SIZE)
    
    # vector_db
    app.vector_db_client = vecttor_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()
    
    # template
    app.template_parser = TemplateParser(languag= settings.PRIMARY_LANGUAGE,
                                         default_language=settings.DEFAULT_LANGUAGE)

    yield
    
    # code here will run after shutdown
    # closing the connection
    app.mongo_conn.close()
    app.vector_db_client.disconnect()

app = FastAPI(lifespan = lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
