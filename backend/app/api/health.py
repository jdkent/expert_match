from fastapi import APIRouter, HTTPException, Request

from app.db.session import check_database_connection

router = APIRouter()


@router.get("/healthz")
async def healthz(request: Request) -> dict[str, str]:
    return {
        "status": "ok",
        "database": "configured" if request.app.state.database_configured else "not_configured",
    }


@router.get("/readyz")
async def readyz(request: Request) -> dict[str, str]:
    if not request.app.state.database_configured:
        return {"status": "ready", "database": "not_configured"}
    if not check_database_connection(request.app.state.settings):
        raise HTTPException(status_code=503, detail="Database is not reachable")
    return {"status": "ready", "database": "ready"}
