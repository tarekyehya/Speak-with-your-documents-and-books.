from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnum, DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_chars: int=1000,
                 default_generation_max_output_tokens: int=1000,
                 temperature: float=0.2):
        
        self.api_key = api_key
   
        
        self.default_generation_input_max_chars = default_input_max_chars
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = temperature
        
        self.generation_model_id = None
        
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.Client(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)
        

    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id 
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
        
    def process_text(self,text: str):
        return text[:self.default_generation_input_max_chars].strip()
    
    
    # edit to work woth cohere
    def generate_text(self, prompt: str,chat_history: list=[], max_output_tokens: str=None,
                      temperature: str = None):
        # assume we wont use it for genertation
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message = self.construct_prompt(prompt=prompt,role=CoHereEnum.USER.value),
            max_tokens = max_output_tokens,
            temperature =temperature
        )
        
        if not response or not response.text or len(response.text) == 0:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        return response.text
    
    
    def embed_text(self, text: str, document_type: str = None):
        # validation
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        input_type = CoHereEnum.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnum.QUERY.value
        
        
        response = self.client.embed(texts = text, # may need to truncate ?
                                                 model=self.embedding_model_id,
                                                  embedding_types=['float'],
                                                  input_type=input_type
                                                  )  
        
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        
        return response.embeddings.float[0]
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
    
    
            
            
    
    
