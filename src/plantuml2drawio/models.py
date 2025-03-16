"""Data models for diagram elements.

This module contains the base classes for diagram elements that are used
across different diagram types.
"""


class Node:
    """Base class for diagram nodes.

    A node represents any element in a diagram (activity, class, component, etc.).

    Attributes:
        id: Unique identifier for the node.
        label: Text label for the node.
        type: Type of node specific to the diagram type.
        x: X-coordinate position.
        y: Y-coordinate position.
        width: Width of the node.
        height: Height of the node.
    """

    def __init__(
        self,
        node_id: str,
        label: str,
        node_type: str,
        x: int = 0,
        y: int = 0,
        width: int = 120,
        height: int = 60,
    ):
        """Initialize a node.

        Args:
            node_id: Unique identifier for the node.
            label: Text label for the node.
            node_type: Type of node specific to the diagram type.
            x: X-coordinate position.
            y: Y-coordinate position.
            width: Width of the node.
            height: Height of the node.
        """
        self.id = node_id
        self.label = label
        self.type = node_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Edge:
    """Base class for diagram edges.

    An edge represents a connection or relationship between two nodes.

    Attributes:
        id: Unique identifier for the edge.
        source: ID of the source node.
        target: ID of the target node.
        label: Optional label for the edge.
    """

    def __init__(self, source: str, target: str, label: str = ""):
        """Initialize an edge.

        Args:
            source: ID of the source node.
            target: ID of the target node.
            label: Optional label for the edge.
        """
        self.id = f"{source}_{target}"
        self.source = source
        self.target = target
        self.label = label
