from abc import ABC, abstractmethod

from pydantic import BaseModel


class DataModel(BaseModel):
    """
    Abstract class for all data models
    """

    entry_id: str | int # Allow int IDs from DB, will be populated from 'data'
    type: str # Set based on table by dispatcher
    table: str # Added: Name of the source table from CDC envelope
    operation: str # Added: DB operation (INSERT, UPDATE, DELETE) from CDC envelope


class VectorDBDataModel(ABC, DataModel):
    """
    Abstract class for all data models that need to be saved into a vector DB (e.g. Qdrant)
    """

    entry_id: int
    type: str

    @abstractmethod
    def to_payload(self) -> tuple:
        pass
