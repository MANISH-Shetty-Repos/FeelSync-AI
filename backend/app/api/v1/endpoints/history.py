from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Any, List, Optional
from ....services.history_service import history_service
from ..deps import get_current_user
from ....models.user import UserOut

router = APIRouter()

@router.get("/", response_model=List[Any])
async def read_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    input_type: Optional[str] = None,
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Retrieve past emotional analyses for the current user.
    """
    return await history_service.get_user_history(
        str(current_user["_id"]), 
        skip=skip, 
        limit=limit, 
        input_type=input_type
    )

@router.get("/stats")
async def read_stats(
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Get aggregated emotional statistics for the dashboard.
    """
    return await history_service.get_emotional_stats(str(current_user["_id"]))

@router.get("/{analysis_id}")
async def read_analysis_detail(
    analysis_id: str,
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Get details of a specific past analysis.
    """
    result = await history_service.get_analysis_by_id(analysis_id, str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result
