from bson import ObjectId
from ..db.mongodb import get_database
from ..models.user import UserInDB, UserCreate
from ..core.security import get_password_hash

async def get_user_by_id(user_id: str):
    db = get_database()
    if db is None:
        return None
    
    # Try searching with ObjectId first (Native MongoDB)
    try:
        obj_id = ObjectId(user_id)
        user_data = await db.users.find_one({"_id": obj_id})
        if user_data:
            return user_data
    except Exception:
        pass
    
    # Fallback: Search with string ID (For users saved as strings during transition)
    user_data = await db.users.find_one({"_id": user_id})
    return user_data

async def get_user_by_email(email: str):
    db = get_database()
    user_data = await db.users.find_one({"email": email})
    return user_data

async def get_user_by_username(username: str):
    db = get_database()
    user_data = await db.users.find_one({"username": username})
    return user_data

async def create_user(user_in: UserCreate):
    db = get_database()
    hashed_password = get_password_hash(user_in.password)
    user_dict = user_in.model_dump()
    user_dict.pop("password")
    
    user_db = UserInDB(
        **user_dict,
        hashed_password=hashed_password
    )
    
    result = await db.users.insert_one(user_db.model_dump(by_alias=True))
    user_data = await db.users.find_one({"_id": result.inserted_id})
    return user_data
