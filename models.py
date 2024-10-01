from pydantic import BaseModel
from bson import ObjectId


class DataModel(BaseModel):
    _id: ObjectId
    first_name: str
    last_name: str
    age: int 
    email: str 
    gender: str 