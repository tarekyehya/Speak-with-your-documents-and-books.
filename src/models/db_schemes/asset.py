from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(...,min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0,default = None)
    asset_config: dict = Field(default = None)
    asset_pushed_at: datetime = Field(default=datetime.now(timezone.utc))
    
    # to avoid treate with ObjectId data type
    class Config:
        arbitrary_types_allowed = True
        
        
    def dict_with_defaults(self):
        # Ensure asset_pushed_at is always present
        data = self.dict(by_alias=True, exclude_unset=True)
        if 'asset_pushed_at' not in data or data['asset_pushed_at'] is None:
            data['asset_pushed_at'] = datetime.now(timezone.utc)
        return data
    
    
        
    @staticmethod
    def get_indexes():
        
        return [
            {
            
            "key":[
                ("asset_project_id",1)
            ],
            "name": "asset_project_id_index_1",
            "unique": False
            
        },
        {
            
            "key":[
                ("asset_project_id",1),
                ("asset_name",1)
            ],
            "name": "asset_project_id_name_index_1",
            "unique": True
            
        }
            ]
    