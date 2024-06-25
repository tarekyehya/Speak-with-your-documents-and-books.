from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)
    
    @field_validator('project_id')
    @classmethod
    def project_id_must_be_alphanumeric(cls,project_id: str):
        if not project_id.isalnum:
            raise ValueError("project is must be alphanumeric (chars or nums)")
        return project_id
    
    # to avoid treate with ObjectId data type
    class Config:
        arbitrary_types_allowed = True
        
    @staticmethod
    def get_indexes():
        
        return [
            {
            
            "key":[
                ("project_id",1)
            ],
            "name": "project_id_index_1",
            "unique": True
            
        }
            ]

    
