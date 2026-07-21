from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import Base, engine
from app.core.exceptions import register_exception_handlers
from app.modules.auth.router import router as auth_router
from app.modules.meals.router import router as meals_router
from app.modules.search.router import router as search_router
from app.modules.swaps.router import router as swaps_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # MVP convenience. Replace with Alembic migrations before deployment.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        # `create_all` does not add columns to existing MVP databases.
        await connection.execute(text("ALTER TABLE meals ADD COLUMN IF NOT EXISTS location VARCHAR(255)"))
    yield
    await engine.dispose()


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TableSwap API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(meals_router, prefix=api_prefix)
app.include_router(search_router, prefix=api_prefix)
app.include_router(swaps_router, prefix=api_prefix)

@app.get("/health", tags=["system"])
async def health_check():
    return {"data": {"status": "ok"}, "meta": {}}
