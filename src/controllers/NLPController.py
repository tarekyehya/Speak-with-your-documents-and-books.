from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json

class NLPController(BaseController):
    # vector db, LLM, mongo db (chunkModel, ProjectModel)
    def __init__(self,vectordb_client, generation_client, embedding_client):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        
    def create_collection_name(self,project_id: str):

        return f"collection_{project_id}".strip()
    
    def reset_vectordb_collection(self,project: Project):
        collection_name = self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name)
        
        # self.vectordb_client.create_collection(collection_name, project.embedding_size, True)
    
    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info =  self.vectordb_client.get_collection_info(collection_name)
        
        return json.loads(
            json.dumps(collection_info, default= lambda x: x.__dict__)
        )
        
    
    def index_into_vectordb(self,project: Project, chunks: List[DataChunk], do_reset: bool = False, batch_size: int = 50):
        # get collection name
        collection_name = self.create_collection_name(project_id = project.project_id)

        # manage items
        texts = [chunk.chunk_text for chunk in chunks]
        vectors = [self.embedding_client.embed_text(
            text = text,
            document_type = DocumentTypeEnum.DOCUMENT.value
            ) for text in texts]

        metadatas = [chunk.chunk_metadata for chunk in chunks]

        # create collection if not exists.
        _ = self.vectordb_client.create_collection(
            collection_name = collection_name,
            embeddeding_size = self.embedding_client.embedding_size,
            do_reset = do_reset 
        )
        
        print(_)
                
        # insert items
        success = self.vectordb_client.insert_many(collection_name = collection_name,
                                                   texts = texts,
                                                   vectors = vectors,
                                                   metadatas = metadatas,
                                                   batch_size=batch_size)

        return success
    
    def search_by_query_in_collection_vectordb(self, project: Project, query: str, top_k: int = 5):
        
        collection_name = self.create_collection_name(project_id = project.project_id)
        
        vector = self.embedding_client.embed_text(text = query,
                                                  document_type = DocumentTypeEnum.QUERY.value)
        
        if not vector or len(vector) == 0:
            return False

        search_results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            top_k=top_k
            )
        
        if not search_results:
            return False

        return json.loads(
            json.dumps(search_results, default= lambda x: x.__dict__)
        )
        
        