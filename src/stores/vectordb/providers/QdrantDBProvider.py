from types import List
from qdrant_client import QdrantClient, models
from ..VectorDBInterface import VectorDBInterface
from..VectorDBEnums import VectorDBEnums, DistanceMethodEnum
from typing import List

import logging

class QdrantDB(VectorDBInterface):
    def __init__(self, db_path: str,
                 Distance_method: str):
        self.client = None
        self.db_path = db_path
        self.distance_method = None
        
        if Distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif Distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        try:
            self.client = QdrantClient(self.db_path)
            self.logger.info(f"Connected to Qdrant DB: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant DB: {self.db_path}. Error: {str(e)}")
            
    
    def disconnect(self):
        self.client = None
    
    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name) # TODO: Validate connection
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str) -> bool:
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    
    
    def create_collection(self, collection_name: str,
                          embeddeding_size: int,
                          do_reset: bool) -> bool:
        
        if not self.client:
            self.logger.error("Qdrant client was not set")
            return False 
    

        if embeddeding_size <= 0:
            self.logger.error("Embeddeding size must be greater than 0")
            return False # no embed
        
        if do_reset:
            self.delete_collection(collection_name=collection_name)
            
        # may do reset = False
        if not self.is_collection_exists(collection_name):
            self.logger.info(f"Creating new collection: {collection_name}")
            self.client.create_collection(
                name=collection_name,
                vector_size=embeddeding_size,
                distance=self.distance_method
                )
            return True  # collection created successfully
            
        else:
            self.logger.info(f"Collection already exists: {collection_name}")
        
        return False 
        
    
    def insert_one(self, collection_name: str, text: str ,vector: List[float],
                   metadata: dict = None,
                   record_id: str = None) -> bool:
        if not self.client:
            self.logger.error("Qdrant client was not set")
            return False
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection does not exist: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={
                            'text' : text,
                            'metadata' : metadata
                            
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Failed to insert record into collection: {collection_name}. Error: {str(e)}")
            return False  # insert failed
            
        return True
    
    def insert_many(self, collection_name: str, texts: List[str], vectors: List[List[float]],
                    metadatas: List[dict] = None,
                    record_ids: List[str] = None, # will not be used for Qdrant
                    batch_size: int = 50) -> bool:
        
        if not self.client:
            self.logger.error("Qdrant client was not set")
            return False
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection does not exist: {collection_name}")
            return False
        
        if metadatas is None:
            metadatas = [None]*len(texts)
        
        for i in range(0, len(texts),batch_size):
            
            batch_end = i + batch_size
            if batch_end > len(texts):
                batch_end = len(texts)
            
            batch_text = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            
            batch_records = [
                models.Record(
                    vector=batch_vectors[x],
                    payload={
                        'text' : batch_text[x],
                        'metadata' : batch_metadatas[x]
                        
                    }
                )
                for x in range(len(batch_vectors))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Failed to insert batch of records into collection: {collection_name}. Error: {str(e)}")
                return False  # insert failed
        
        return True
    
    
    def search_by_vector(self, collection_name: str, vector: List[float], top_k: int = 5) -> List:
        # TODO:validation here
        return self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit = top_k
            )
                    
        
        
        