from enum import Enum

class ResponseMassages(Enum):


    FILE_validate_SUCCESS = "file validate success"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_PROCESSING_FAILED = "processing_file_failed" 
    FILE_PROCESSING_SUCCESS = "processing_file_success"
    FILE_NO_FILES_ERROR = "not_found_files"
    FILE__NAME_INCORRECT = "the file name is not correct"
    
     