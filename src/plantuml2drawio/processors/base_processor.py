"""Base class for diagram processors."""

from abc import ABC, abstractmethod


class BaseDiagramProcessor(ABC):
    """Base class for all diagram processors."""

    @abstractmethod
    def is_valid_diagram(self, content: str) -> bool:
        """Check if the diagram content can be processed by this processor."""
        pass

    @abstractmethod
    def convert_to_drawio(self, content: str) -> str:
        """Convert the PlantUML diagram to Draw.io format."""
        pass
