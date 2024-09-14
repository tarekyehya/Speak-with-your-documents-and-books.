from enum import Enum

class LLMEnums(Enum):
    OPENAI = 'OPENAI'
    COHERE = 'COHERE'
    
class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    
class CoHereEnum(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    
    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnum(Enum):
    QUERY = "query"
    DOCUMENT = "document"