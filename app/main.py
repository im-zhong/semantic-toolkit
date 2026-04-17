from fastapi import FastAPI

app = FastAPI(title="Semantic Toolkit")


@app.get("/")
def read_root():
    return {"message": "Hello from Semantic Toolkit"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
