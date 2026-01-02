from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.forward import router as forward_router
from app.routes.history import router as history_router
from app.routes.stats import router as stats_router

app = FastAPI(title="ML Service")

app.include_router(auth_router)
app.include_router(forward_router)
app.include_router(history_router)
app.include_router(stats_router)
