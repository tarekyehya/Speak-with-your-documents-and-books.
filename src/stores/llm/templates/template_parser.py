import os

class TemplateParser:
    def __init__(self, languag: str = None, default_language: str = 'en'):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        
        # set language
        self.set_language(languag)
        
    
    # to can change the language after taking the anstance
    def set_language(self, language: str):
        if not language:
            self.language = self.default_language
            return None
        
        # if the language is exist:
        language_path = os.path.join(self.current_path,'locales', language)
        if os.path.exists(language_path):
            self.language = language
        
        else:
            self.language = self.default_language
        
        return None
    
    def get(self, group: str, key: str, vars: dict = {}):
        if not group or not key:
            return None
        
        # now the path is exist because the language is supported 
        
        
        # import group module, at runtime
        module  = __import__(f"stores.llm.templates.locales.{self.language}.{group}", fromlist=[group])
        
        if not module:
            return None
        
        key_attributes = getattr(module,key)
        
        return key_attributes.substitute(vars)
    
                
        
         
        