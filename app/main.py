from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import organizations, buildings, activities
from app.database import engine, Base
from app.seed_data import seed_data

Base.metadata.create_all(bind=engine)
seed_data()


app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organizations.router, prefix="/api/v1")
app.include_router(buildings.router, prefix="/api/v1")
app.include_router(activities.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "docs": "/docs",
        "redoc": "/redoc"
    }
