from typing import Optional
from ..db.mongodb import get_database
from ..models.user import UserInDB, UserCreate
from ..core.security import get_password_hash

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
