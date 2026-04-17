"""
Custom exceptions for the application - enables specific error handling.
"""


class DocQueryException(Exception):
    """Base exception for DocQuery application."""
    pass


class DocumentProcessingError(DocQueryException):
    """Raised when document processing fails."""
    pass


class EmbeddingError(DocQueryException):
    """Raised when text embedding fails."""
    pass


class VectorStoreError(DocQueryException):
    """Raised when vector store operations fail."""
    pass


class InvalidDocumentError(DocQueryException):
    """Raised when document is invalid or unsupported."""
    pass


class FileSizeExceededError(DocQueryException):
    """Raised when file exceeds maximum size limit."""
    pass


class ServiceUnavailableError(DocQueryException):
    """Raised when required service is not initialized."""
    pass
