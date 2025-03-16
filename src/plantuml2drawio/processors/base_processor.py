"""Base class for diagram processors."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Type

from plantuml2drawio.models import Edge, Node


class BaseDiagramProcessor(ABC):
    """Base class for all diagram processors."""

    @classmethod
    @abstractmethod
    def detect_diagram_type(cls, content: str) -> float:
        """Detect if the content is a diagram of this processor's type.

        Args:
            content: PlantUML content to analyze

        Returns:
            A confidence score between 0.0 and 1.0 where:
            - 0.0 means definitely not this diagram type
            - 1.0 means definitely this diagram type
            - Values in between represent uncertainty
        """
        pass

    @abstractmethod
    def is_valid_diagram(self, content: str) -> bool:
        """Check if the diagram content can be processed by this processor."""
        pass

    @abstractmethod
    def parse_diagram(self, content: str) -> Tuple[List[Node], List[Edge]]:
        """Parse the PlantUML content into lists of nodes and edges.

        Args:
            content: PlantUML content to parse

        Returns:
            A tuple containing:
            - nodes: List of Node objects representing diagram elements
            - edges: List of Edge objects representing connections
        """
        pass

    @abstractmethod
    def layout_diagram(self, nodes: List[Node], edges: List[Edge]) -> None:
        """Calculate the layout for the diagram elements.

        This function modifies the nodes in place by setting their x, y, width,
        and height properties.

        Args:
            nodes: List of Node objects
            edges: List of Edge objects
        """
        pass

    @abstractmethod
    def export_to_drawio(self, nodes: List[Node], edges: List[Edge]) -> str:
        """Export the diagram to Draw.io XML format.

        Args:
            nodes: List of Node objects
            edges: List of Edge objects

        Returns:
            String containing the Draw.io XML representation
        """
        pass

    def convert_to_drawio(self, content: str) -> str:
        """Convert the PlantUML diagram to Draw.io format.

        This method follows the standard process flow:
        1. Parse the diagram to get nodes and edges
        2. Layout the nodes based on their relationships
        3. Export to Draw.io XML format

        Args:
            content: The PlantUML diagram content to convert.

        Returns:
            The diagram converted to Draw.io XML format.
        """
        # Step 1: Parse the diagram
        nodes, edges = self.parse_diagram(content)

        # Step 2: Layout the diagram
        self.layout_diagram(nodes, edges)

        # Step 3: Export to Draw.io XML format
        return self.export_to_drawio(nodes, edges)

    def convert_to_json(self, content: str) -> str:
        """Convert the PlantUML diagram to JSON representation.

        Args:
            content: PlantUML content to convert

        Returns:
            JSON string representing the diagram
        """
        # Parse the diagram
        nodes, edges = self.parse_diagram(content)

        # Layout the diagram
        self.layout_diagram(nodes, edges)

        # Create a simple JSON representation
        import json

        diagram_data = {
            "nodes": [self._node_to_dict(node) for node in nodes],
            "edges": [self._edge_to_dict(edge) for edge in edges],
        }

        return json.dumps(diagram_data, indent=2)

    def _node_to_dict(self, node: Node) -> Dict:
        """Convert a node to a dictionary.

        This is a helper method for JSON serialization. It should be overridden
        by subclasses if needed.

        Args:
            node: Node object

        Returns:
            Dictionary representation of the node
        """
        return {
            "id": node.id,
            "label": node.label,
            "type": node.type,
            "x": node.x,
            "y": node.y,
            "width": node.width,
            "height": node.height,
        }

    def _edge_to_dict(self, edge: Edge) -> Dict:
        """Convert an edge to a dictionary.

        This is a helper method for JSON serialization. It should be overridden
        by subclasses if needed.

        Args:
            edge: Edge object

        Returns:
            Dictionary representation of the edge
        """
        return {
            "id": f"{edge.source}_{edge.target}",
            "source": edge.source,
            "target": edge.target,
            "label": edge.label,
        }


class ProcessorRegistry:
    """Registry for diagram processors."""

    _processors: Dict[str, Type[BaseDiagramProcessor]] = {}

    @classmethod
    def register(
        cls, diagram_type: str, processor_class: Type[BaseDiagramProcessor]
    ) -> None:
        """Register a processor for a specific diagram type.

        Args:
            diagram_type: Type identifier for the diagram
            processor_class: Class that processes this diagram type
        """
        cls._processors[diagram_type] = processor_class

    @classmethod
    def get_processor(cls, diagram_type: str) -> Optional[Type[BaseDiagramProcessor]]:
        """Get processor class for a specific diagram type.

        Args:
            diagram_type: Type identifier for the diagram

        Returns:
            Processor class for the diagram type or None if not found
        """
        return cls._processors.get(diagram_type)

    @classmethod
    def get_all_processors(cls) -> Dict[str, Type[BaseDiagramProcessor]]:
        """Get all registered processors.

        Returns:
            Dictionary mapping diagram types to processor classes
        """
        return cls._processors

    @classmethod
    def detect_diagram_type(
        cls, content: str
    ) -> Tuple[str, Type[BaseDiagramProcessor]]:
        """Detect the diagram type from the content.

        Args:
            content: PlantUML content to analyze

        Returns:
            Tuple of (diagram_type, processor_class) for the detected diagram
            If no suitable processor is found, returns ("unknown", None)
        """
        if not content or "@startuml" not in content or "@enduml" not in content:
            return "not_plantuml", None

        # Find the processor with the highest confidence
        max_confidence = 0.0
        best_type = "unknown"
        best_processor = None

        for diagram_type, processor_class in cls._processors.items():
            confidence = processor_class.detect_diagram_type(content)
            if confidence > max_confidence:
                max_confidence = confidence
                best_type = diagram_type
                best_processor = processor_class

        return best_type, best_processor
