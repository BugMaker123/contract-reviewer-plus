import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contract_app.bootstrap.config import settings
from contract_app.shared.errors import DomainError
from contract_app.http.contracts_router import router as contracts_router
from contract_app.http.sessions_router import router as sessions_router
from contract_app.http.reviews_router import router as reviews_router
from contract_app.http.decisions_router import router as decisions_router
from contract_app.http.exports_router import router as exports_router
from contract_app.http.categories_router import router as categories_router
from contract_app.http.checklists_router import router as checklists_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="在线合同智能审查与修订系统后端服务",
        version="1.0.0",
        debug=settings.debug
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        req_id = request.headers.get("X-Request-Id", f"req_{uuid.uuid4().hex[:8]}")
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": req_id,
                    "retryable": exc.retryable,
                    "details": exc.details
                }
            }
        )

    # Register routers under api_prefix
    api_prefix = settings.api_prefix
    app.include_router(contracts_router, prefix=api_prefix)
    app.include_router(sessions_router, prefix=api_prefix)
    app.include_router(reviews_router, prefix=api_prefix)
    app.include_router(decisions_router, prefix=api_prefix)
    app.include_router(exports_router, prefix=api_prefix)
    app.include_router(categories_router, prefix=api_prefix)
    app.include_router(checklists_router, prefix=api_prefix)

    @app.get("/health")
    @app.get(f"{api_prefix}/health")
    async def health_check():
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": "1.0.0"
        }

    return app

app = create_app()
