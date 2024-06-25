from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enum.DataBaseEnum import DataBaseEnum
from bson import ObjectId

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
    
    async def get_all_project_assets(self, asset_project_id: str):
        return await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id)
        }).to_list(length=None)