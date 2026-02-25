from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import configs, versions, evaluations


# 创建数据库表
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(configs.router, prefix="/api/configs", tags=["configs"])
app.include_router(versions.router, prefix="/api/versions", tags=["versions"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])


@app.get("/")
def root():
    return {"message": "Eval Platform API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
