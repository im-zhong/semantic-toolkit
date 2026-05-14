from fastapi import FastAPI

from auto_classifier.config import API_DESCRIPTION, API_TITLE, API_VERSION
from auto_classifier.routers import classify, health

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

app.include_router(health.router)
app.include_router(classify.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("auto_classifier.main:app", host="0.0.0.0", port=8000, reload=True)