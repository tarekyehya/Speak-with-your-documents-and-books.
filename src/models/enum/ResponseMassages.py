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
    PROJECT_NOT_FOUND = "project_not_found"
    INSERT_INTO_VECTORDB_ERROR = "insert_in_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert_in_vectordb_success"
    GET_VECTORDB_INFO_SUCCESS = "get_vectordb_info_success"
    GET_VECTORDB_INFO_failed = "get_vectordb_info_failed"
    VECTORDB_COLLECTION_NOT_EXISTS = "collection_not_exists"
    SEARCH_IN_VECTORDB_SUCCESS = "search_in_vectordb_success"
    SEARCH_IN_VECTORDB_FAILED = "search_in_vectordb_failed"
    RAG_ANSWER_FAILED = "answer_query_failed"
    RAG_ANSWER_SUCCESS = "answer_query_success"
    