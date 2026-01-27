from input_output.interfaces import IFileHandler
from model.tag_model import TagModel
from utils.interfaces import ITagProcessor


class DocumentManager():
    def __init__(self,file_handler:IFileHandler,tag_processor:ITagProcessor)-> None:
        """
        Initializes the DocumentManager with a FileHandler and TagProcessor instance.
        Args:
            file_handler (IFileHandler): Used to read and write document files.
            tag_processor (ITagProcessor): Used to process tags within document text.
        """
        self._file_handler = file_handler
        self._tag_processor = tag_processor

    def save_document(self,file_path:str, document:dict, view_id:str)-> bool:
        """
        Saves the given document to the specified file path.
        Args:
            file_path (str): The path where the document should be saved.
            document (dict): The document data to be saved.
            view_id (str): The active view identifier (e.g., 'annotation', 'comparison').
        Returns:
            bool: True if the document was saved successfully, False otherwise.
        """
        # Prepare document data based on view type
        if not view_id == "comparison":
            if "text" in document:
                inline_text=document.pop("text")
                plain_tags_and_tags=self._tag_processor.get_plain_text_and_tags(inline_text)
                document["plain_text"]=plain_tags_and_tags["plain_text"]
                document["tags"]=plain_tags_and_tags["tags"]
            elif "plain_text" not in document or "tags" not in document:
                raise ValueError(
                    "Document must contain either 'text' or both 'plain_text' and 'tags' for saving.")
            document_data = {"document_type": view_id,
                             "file_path": file_path,
                             "file_name": document["file_name"],
                             "meta_tags": {
                                 tag_type: [
                                     ", ".join(str(tag) for tag in tags)]
                                 for tag_type, tags in document.get("meta_tags", {}).items()
                             },
                             "plain_text": document["plain_text"],
                             "tags": document["tags"],
                             "schema_version": 2
                             }
        else:
            # prepare data for comparison view
            old_comparison_sentences=document.get("comparison_sentences",[])
            new_comparison_sentences=[]
            for old_version in old_comparison_sentences:
                new_version=[]
                for inline_text in old_version:
                    sentence_data={}
                    plain_tags_and_tags=self._tag_processor.get_plain_text_and_tags(inline_text)
                    sentence_data["plain_text"]=plain_tags_and_tags["plain_text"]
                    sentence_data["tags"]=plain_tags_and_tags["tags"]
                    new_version.append(sentence_data)
                new_comparison_sentences.append(new_version)


            merged_document_data = {}
            merged_document = document.get("merged_document", {})
            merged_document_data["file_name"]=merged_document.get_file_name()
            merged_document_data["file_path"]=merged_document.get_file_path()
            merged_document_data["meta_tags"]={
                tag_type: [", ".join(str(tag) for tag in tags)]
                for tag_type, tags in merged_document.get_meta_tags().items()
            }
            inline_text=merged_document.get_text()
            plain_tags_and_tags=self._tag_processor.get_plain_text_and_tags(inline_text)
            merged_document_data["plain_text"]=plain_tags_and_tags["plain_text"]
            merged_document_data["tags"]=plain_tags_and_tags["tags"]

            document_data = {
                "document_type": "comparison",
                "source_paths": document["source_file_paths"],
                "source_file_names": document.get("file_names", []),
                "file_path": file_path,
                "num_sentences": document.get("num_sentences", 0),
                "current_sentence_index": document.get("current_sentence_index", 0),
                "comparison_sentences": new_comparison_sentences,
                "adopted_flags": document.get("adopted_flags", []),
                "differing_to_global": document.get("differing_to_global", []),
                "merged_document_data": merged_document_data,
                "schema_version": 2
                }
            

        if document_data:
            success = self._file_handler.write_file(file_path, document_data)
            return success
        else:
            raise ValueError(
                "No valid document data found for saving. Ensure the active view is set correctly.")


    def load_document(self, file_path)->dict:
        """
        Loads a document from the given file path and transforms it to the internal schema if needed.
        Args:
            file_path (str): The path to the document file.
        Returns:
            dict: The loaded document in internal schema.
        """
        document = self._file_handler.read_file(
            file_path=file_path)
        document["file_path"] = file_path

        transformed_document_data = self._transform_document_to_internal_schema(document)

        if document.get("schema_version", 1) >= 2:
            document_data = self._add_tags_to_loaded_document(transformed_document_data,document)
        else:
            document_data = self._add_tags_to_loaded_document(transformed_document_data)
        return document_data
    
    def import_plain_text_document(self, file_path)->dict:
        """
        Imports a plain text document from the given file path and wraps it in the internal schema.
        Args:
            file_path (str): The path to the plain text document.
        Returns:
            dict: The imported document in internal schema.
        """
        text = self._file_handler.read_file(
            file_path=file_path)
        document = {
            "document_type": "annotation",
            "file_path": file_path,
            "file_name": self._file_handler.derive_file_name(file_path),
            "meta_tags": {},
            "text": text
        }
        return document
    
    def _transform_document_to_internal_schema(self, document: dict) -> dict:
        """
        Transforms a loaded document to the internal schema used by the application.
        Args:
            document (dict): The loaded document.
        Returns:
            dict: The transformed document.
        """
        schema_version = document.get("schema_version", 1)
        if schema_version >= 2:
            if document.get("document_type") == "comparison":
                # Transform comparison document structure
                transformed_document = {
                    "document_type": "comparison",
                    "file_name": document.get("file_name", ""),
                    "source_paths": document.get("source_paths", []),
                    "source_file_names": document.get("source_file_names", []),
                    "file_path": document.get("file_path", ""),
                    "num_sentences": document.get("num_sentences", 0),
                    "current_sentence_index": document.get("current_sentence_index", 0),
                    "comparison_sentences": [],
                    "adopted_flags": document.get("adopted_flags", []),
                    "differing_to_global": document.get("differing_to_global", []),
                    "merged_document_data": {}
                }
                for sentence_group in document.get("comparison_sentences", []):
                    transformed_group = []
                    for sentence in sentence_group:
                        inline_text = self._tag_processor.merge_plain_text_and_tags(
                            sentence.get("plain_text", ""),
                            sentence.get("tags",[])
                        )
                        transformed_group.append(inline_text)
                    transformed_document["comparison_sentences"].append(transformed_group)

                old_merged_document_data = document.get("merged_document_data", {})
                merged_inline_text = self._tag_processor.merge_plain_text_and_tags(
                    old_merged_document_data.get("plain_text", ""),
                    old_merged_document_data.get("tags", [])
                )
                new_merged_document_data = {
                    "document":{
                        "file_name": old_merged_document_data.get("file_name", ""),
                        "file_path": old_merged_document_data.get("file_path", ""),
                        "meta_tags": {
                            tag_type: [tag.strip() for tag in tags_str.split(",")]
                            for tag_type, tags_str in old_merged_document_data.get("meta_tags", {}).items()
                        },
                        "text": merged_inline_text
                    }
                }
                transformed_document["merged_document_data"] = new_merged_document_data
                data={
                    "document": transformed_document,
                }

            elif document.get("document_type") == "annotation":
                inline_text = self._tag_processor.merge_plain_text_and_tags(
                    document.get("plain_text", ""),
                    document.get("tags", [])
                )
                transformed_document = {
                    "document_type": "annotation",
                    "file_path": document.get("file_path", ""),
                    "file_name": document.get("file_name", ""),
                    "meta_tags": {
                        tag_type: [tag.strip() for tag in tags_str.split(",")]
                        for tag_type, tags_str in document.get("meta_tags", {}).items()
                    },
                    "text": inline_text,

                }
                data={
                    "document": transformed_document,
                }
            elif document.get("document_type") == "extraction":
                raise ValueError(
                    "Extraction document type is not needed to be transformed.")
            else:
                raise ValueError(
                    f"Unknown document type: {document.get('document_type')}")
        else:#schema 1
            data = {
                "document": document
            }
            if document.get("document_type") == "comparison":
                data["document"]["merged_document_data"] = {"document": data["document"]["merged_document_data"]}
        return data
            
    def _add_tags_to_loaded_document(self, new_document_data: dict, old_document_data: dict=None) -> dict:
        if new_document_data["document"].get("document_type") == "annotation":
            if old_document_data: #schema >=2
                tags = old_document_data.get("tags", [])
            else: #schema 1
                document_text = new_document_data["document"]["text"]
                tags = self._tag_processor._extract_tags_from_text(document_text)
            new_document_data["tags"] = [TagModel(tag) for tag in tags]
        elif new_document_data["document"].get("document_type") == "comparison":
            if old_document_data: #schema >=2
                merged_document_tags = old_document_data.get("merged_document_data", {}).get("tags", [])
                comparison_sentences = old_document_data.get("comparison_sentences", [])
                comparison_tags = [[sentence.get("tags", []) for sentence in group] for group in comparison_sentences]
            else: #schema 1
                merged_document_text = new_document_data["document"]["merged_document_data"]["document"]["text"]
                merged_document_tags = self._tag_processor._extract_tags_from_text(merged_document_text)
                comparison_sentences = new_document_data["document"]["comparison_sentences"]
                comparison_tags = []
                for sentence_group in comparison_sentences:
                    comparison_tags_group = []
                    for inline_text in sentence_group:
                        tags = self._tag_processor._extract_tags_from_text(inline_text)
                        comparison_tags_group.append(tags)
                    comparison_tags.append(comparison_tags_group)
            new_document_data["document"]["merged_document_data"]["tags"] = [TagModel(tag) for tag in merged_document_tags]
            new_document_data["comparison_tags"] = [[TagModel(tag) for tag in tag_group] for tag_group in comparison_tags]
        return new_document_data
        

       