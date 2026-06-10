from fastapi import APIRouter

from example_projects.pharmax.Backend.app.api.routes.activity_route import router as activity_router
from example_projects.pharmax.Backend.app.api.routes.auth_route import router as auth_router
from example_projects.pharmax.Backend.app.api.routes.dashboard_route import router as dashboard_router
from example_projects.pharmax.Backend.app.api.routes.invoices_route import router as invoices_router
from example_projects.pharmax.Backend.app.api.routes.products_route import router as products_router
from example_projects.pharmax.Backend.app.api.routes.users_route import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(activity_router, prefix="/activity-logs", tags=["activity-logs"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(products_router, tags=["products"])
api_router.include_router(invoices_router, prefix="/invoices", tags=["invoices"])
