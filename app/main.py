from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import snippets
from app.services.database import create_tables

# Create FastAPI instance
app = FastAPI(
    title="DevSnippets API",
    description="Semantic code search API for developers",
    version="1.0.0"
)

# Configure CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(snippets.router, prefix="/api", tags=["snippets"])

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "DevSnippets API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}