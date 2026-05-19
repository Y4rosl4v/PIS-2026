from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.adapter.in.course_controller import router
from app.infrastructure.config.database import init_db

app = FastAPI(
    title="Quick Courses API",
    description="API for micro-learning platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте"""
    init_db()
    print("Database initialized")

@app.get("/")
async def root():
    return {
        "service": "Quick Courses Platform",
        "version": "1.0.0",
        "docs": "/api/docs"
    }