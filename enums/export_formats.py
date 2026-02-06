from enum import Enum, auto


class ExportFormat(Enum):
    """
    Enumeration of export formats for documents.
    INLINE: Export format with inline tags.
    SPLIT: Export format with tags and text separated.
    """
    INLINE = auto()
    SPLIT = auto()
