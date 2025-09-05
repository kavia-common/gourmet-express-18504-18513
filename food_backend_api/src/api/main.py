import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, restaurants, menus, orders, payments, notifications, profiles
from .core.config import settings
from .core.docs import openapi_tags


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function sets up the application with:
    - CORS middleware
    - OpenAPI metadata and tags
    - Routers for all domain areas
    - Root health check

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Gourmet Express API",
        description=(
            "Backend API for a food delivery platform. Features include authentication, "
            "restaurant catalog, menu browsing, order placement and tracking, payments (mock), "
            "notifications (stub), and user profile management."
        ),
        version="1.0.0",
        contact={"name": "Gourmet Express Team"},
        openapi_tags=openapi_tags,
    )

    # PUBLIC_INTERFACE
    @app.get("/", tags=["Health"], summary="Health Check", description="Returns a simple health status for the API.")
    def health_check():
        """Simple health check endpoint returning API status."""
        return {"status": "ok", "name": "Gourmet Express API", "version": app.version}

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/auth")
    app.include_router(profiles.router, prefix="/profiles")
    app.include_router(restaurants.router, prefix="/restaurants")
    app.include_router(menus.router, prefix="/menus")
    app.include_router(orders.router, prefix="/orders")
    app.include_router(payments.router, prefix="/payments")
    app.include_router(notifications.router, prefix="/notifications")

    return app


app = create_app()

# Convenient runtime config note endpoint
@app.get("/config", tags=["Health"], summary="Runtime config summary", description="Expose non-secret runtime config for diagnostics.")
def get_runtime_config():
    return {
        "environment": os.getenv("ENVIRONMENT", "local"),
        "jwt_algorithm": "HS256",
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "cors_allow_origins": settings.CORS_ALLOW_ORIGINS,
        "mock_mode": True,
    }
