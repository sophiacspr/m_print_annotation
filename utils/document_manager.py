from input_output.interfaces import IFileHandler
from utils.interfaces import ITagProcessor


class DocumentManager():
    def __init__(self,file_handler:IFileHandler,tag_processor:ITagProcessor)-> None:
        self._file_handler = file_handler
        self._tag_processor = tag_processor

    def save_document(self,file_path, document_data)->None:

        pass

    def load_document(self, file_path)->dict:
        document = self._file_handler.read_file(
            file_path=file_path)
        document["file_path"] = file_path

        document = self._upgrade_document_to_v2(document)
        return document
    
    def import_plain_text_document(self, file_path)->dict:
        #todo implement later
        document = self._file_handler.read_file(
            file_path=file_path)
        document["file_path"] = file_path

        # Convert plain text document to version 2 schema
        document = self._setup_document(document)
        return document
    
    def _upgrade_document_to_v2(self, document:dict)->dict:
        if document.get("schema_version", 1) == 2:
            return document

        if document.get("document_type") == "annotation":
            inline_text=document.pop("text","")
            plain_tags_and_tags=self._tag_processor.get_plain_text_and_tags(inline_text)
            document["plain_text"]=plain_tags_and_tags["plain_text"]
            document["tags"]=plain_tags_and_tags["tags"]
            
        elif document.get("document_type") == "comparison":
            pass
            



        document["schema_version"] = 2
        return document