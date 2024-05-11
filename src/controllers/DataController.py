from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseMassages as rs

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024 # bytes -> kilo bytes -> MB


    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, rs.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, rs.FILE_SIZE_EXCEEDED.value
        
        return True, rs.FILE_UPLOD_SUCCESS.value