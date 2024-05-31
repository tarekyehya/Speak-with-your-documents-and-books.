from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1)
    
    @field_validator('project_id')
    @classmethod
    def project_id_must_be_alphanumeric(cls,project_id: str):
        if not project_id.isalnum:
            raise ValueError("project is must be alphanumeric (chars or nums)")
        return project_id
    
    # to avoid treate with ObjectId data type
    class config:
        arbitrary_types_allowed = True

    
