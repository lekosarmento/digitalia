from fastapi import FastAPI
from app.api.v1.routes import webhook, learners, companies

app = FastAPI(
    title="DigitalIA API",
    description="Core Backend API do ecossistema DigitalIA para aprendizado prático e geração de portfólios.",
    version="1.0.0"
)

# Registrar roteadores com versionamento de API V1
app.include_router(webhook.router, prefix="/api/v1", tags=["Webhook"])
app.include_router(learners.router, prefix="/api/v1/learners", tags=["Learners (CRUD)"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies (CRUD)"])

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "DigitalIA API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
