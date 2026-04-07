from fastapi import APIRouter, HTTPException
from database import supabase
from models.goal import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("/")
async def list_goals(
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
):
    query = supabase.table("goals").select("*")
    if status:
        query = query.eq("status", status)
    if priority:
        query = query.eq("priority", priority)
    if category:
        query = query.eq("category", category)
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{goal_id}")
async def get_goal(goal_id: str):
    result = supabase.table("goals").select("*").eq("id", goal_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Goal not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_goal(goal: GoalCreate):
    data = goal.model_dump(exclude_none=True)
    if "target_date" in data and data["target_date"] is not None:
        data["target_date"] = str(data["target_date"])
    result = supabase.table("goals").insert(data).execute()
    return result.data[0]


@router.put("/{goal_id}")
async def update_goal(goal_id: str, goal: GoalUpdate):
    data = goal.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "target_date" in data and data["target_date"] is not None:
        data["target_date"] = str(data["target_date"])
    result = supabase.table("goals").update(data).eq("id", goal_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Goal not found")
    return result.data[0]


@router.delete("/{goal_id}")
async def delete_goal(goal_id: str):
    result = supabase.table("goals").delete().eq("id", goal_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}
