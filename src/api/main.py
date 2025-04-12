from fastapi import FastAPI
from src.api.routers.crawling import router as crawling_router

app = FastAPI()
app.include_router(crawling_router)

@app.get("/")
async def root():
    return {"message": "API is running"}