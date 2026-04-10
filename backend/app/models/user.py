from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId

from pydantic_core import CoreSchema, core_schema
from pydantic.json_schema import JsonSchemaValue

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(ObjectId),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(_core_schema)

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserOut(UserBase):
    id: str = Field(..., alias="_id")
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        from_attributes = True

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return data
        data["_id"] = str(data["_id"])
        return cls(**data)
