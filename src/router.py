from fastapi import APIRouter

from codehub_crawler import router as codehub_router

api_router = APIRouter()
api_router.include_router(codehub_router.router, prefix='/codehub')
