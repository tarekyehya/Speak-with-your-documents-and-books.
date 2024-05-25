from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseMassages as rs
from .ProjectController import ProjectController
import re
import os


class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024 # bytes -> kilo bytes -> MB


    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, rs.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, rs.FILE_SIZE_EXCEEDED.value
        
        return True, rs.FILE_UPLOD_SUCCESS.value # in feature, we will may need to modify the massage, validation true not mean the file uploaded success
     
    def generate_unique_name(self,original_file_name: str, project_id: str):
        
        random_string = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_file_name = self.get_clean_file_name(original_file_name=original_file_name)

        new_file_path = os.path.join(
            project_path,
            random_string + "_" + cleaned_file_name
        )

        # if the path is existed !
        while os.path.exists(new_file_path):
            random_string = self.generate_random_string()
            new_file_path = os.path.join(
            project_path,
            random_string + "_" + cleaned_file_name
        )

        return new_file_path, random_string + "_" + cleaned_file_name

    def get_clean_file_name(self, original_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', original_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
        