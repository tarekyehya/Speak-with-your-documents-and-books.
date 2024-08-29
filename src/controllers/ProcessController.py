from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum

class ProcessController(BaseController):
    
    def __init__(self,project_id: str):
        super().__init__()
        
        self.project_id = project_id 
        self.project_path = ProjectController().get_project_path(project_id=project_id)
    
    def file_extinsion(self,file_name: str):
        extinsion = os.path.splitext(file_name)[-1]
        return extinsion
    
    def get_file_loader(self, file_name: str):
        
        file_ext = self.file_extinsion(file_name=file_name)
        file_path = os.path.join(
            self.project_path,
            file_name
        )
        
        if not os.path.exists(file_path):
            return None
        
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None
        
    def get_file_content(self,file_name: str):
        loader = self.get_file_loader(file_name=file_name)
        if loader:
            return loader.load()
        
        return None # the file is not exist
    
    def process_file_content(self,file_content: list,file_name: str,
                             chunk_size: int=100,overlab_size: int=20):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlab_size,
            length_function=len,
            is_separator_regex=False,
        )
        
        # iterate over pages 
        file_content_texts = [rec.page_content for rec in file_content]
        
        file_content_metadata = [rec.metadata for rec in file_content]
        
        text_chunks = text_splitter.create_documents(
            texts = file_content_texts,
            metadatas = file_content_metadata
            ) 
        
        return text_chunks
        