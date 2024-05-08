from fastapi import FastAPI, APIRouter
import os


base_router = APIRouter()

@base_router.get("/")
async def welcome():
    app_name = os.getenv('APP_NAME')
    version_name = os.getenv('APP_VERSION')

    return {
        "app_name":app_name,
        "version_name": version_name
    }


