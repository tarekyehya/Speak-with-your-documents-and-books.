from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enum.DataBaseEnum import DataBaseEnum
from bson import ObjectId
import logging

# for test internal methods
logger = logging.getLogger("uvicorn.error")

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
        
        
    # we want to call init_collection
    @staticmethod
    async def create_instance(db_client: object):
        instance = AssetModel(db_client)
        await instance.init_collection()
        return instance


    
    # create index
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
        #    self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes() # staticmethod
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                    
                )
                
    
    async def create_asset(self, asset: Asset):
        
        result = await self.collection.insert_one(asset.dict_with_defaults())
        asset.id = result.inserted_id
        
        return asset
    
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        records =  await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id, # convert to ObjectId
            "asset_type" : asset_type
        }).to_list(length=None)
        
        
        return [
            Asset(**record)
            for record in records
        ] # list of records --> in pydantic form
        
        
    async def get_asset_record(self,asset_name : str,asset_project_id : str,asset_type: str):
            record =  await self.collection.find_one({
                "asset_name": asset_name,
                "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id, # convert to ObjectId
                "asset_type" : asset_type
            })
            
            if record:
                return [Asset(**record)] # list to be like the get_all_project_assets return
            return None # to distinguish in the error massage 
     
    
    async def get_assets(self,asset_name : str,asset_project_id : str,asset_type: str):
        """
        general method to return files of the project or only file
        """
        if asset_name:
            return  await self.get_asset_record(asset_name ,asset_project_id,asset_type)
        else:
            
            return await self.get_all_project_assets(asset_project_id, asset_type)
        