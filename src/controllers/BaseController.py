from helpers.config import get_settings, Settings
import os
import random as rn
import string


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()

        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )
        
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
            
        )
    
    def generate_random_string(self, lenght: int = 6):
        return ''.join(rn.choices(string.ascii_lowercase + string.digits, k= lenght))
    
    def get_database_path(self, database_name: str):
        database_dir = os.path.join(
            self.database_dir,
            database_name
        )

        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
        
        return database_dir
    
