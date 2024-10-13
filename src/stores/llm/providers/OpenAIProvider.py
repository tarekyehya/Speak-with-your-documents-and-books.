from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnum
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,api_url: str=None,
                 default_input_max_chars: int=1000,
                 default_generation_max_output_tokens: int=1000,
                 temperature: float=0.2):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_generation_input_max_chars = default_input_max_chars
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = temperature
        
        self.generation_model_id = None
        
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url
        )
        
        self.enums = OpenAIEnum
        
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id 
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
        
    def process_text(self,text: str):
        return text[:self.default_generation_input_max_chars].strip()
    
    
    def generate_text(self, prompt: str,chat_history: list=[], max_output_tokens: str=None,
                      temperature: str = None):
        # assume we wont use it for genertation
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        chat_history.append(
            self.construct_prompt(prompt=prompt,
                                  role=OpenAIEnum.USER.value)
        )
        
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens = max_output_tokens,
            temperature =temperature
        )
        
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message['content']
        
        
    def embed_text(self, text: str, document_type: str = None):
        # validation
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        response = self.client.embeddings.create(input = text,
                                                 model=self.embedding_model_id)  
        
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return response.data[0].embedding
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
    
    