from model.document_model import DocumentModel


class ExtractionDocumentModel(DocumentModel):
    """
    A specialized DocumentModel for managing preview text.
    """

    def __init__(self):
        super().__init__()

    def get_state(self):
        return super().get_state()
