"""Processor for PlantUML activity diagrams."""

import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

from .base_processor import BaseDiagramProcessor

# Predefined regex patterns for better performance
RE_ACTIVITY = re.compile(
    r":\s*(.+?);", re.DOTALL
)  # DOTALL allows newlines in activities
RE_IF_BLOCK = re.compile(r"if\s*\(.+?\).+?endif", re.DOTALL | re.IGNORECASE)


class Node:
    """Represents a node in the activity diagram.

    A node can be an activity, decision, start point, or end point in the diagram.

    Attributes:
        id: Unique identifier for the node.
        label: Text displayed in the node.
        shape: Shape of the node (e.g., "ellipse", "rectangle", "rhombus").
        x: X-coordinate position.
        y: Y-coordinate position.
        width: Width of the node.
        height: Height of the node.
    """

    def __init__(
        self,
        id: str,
        label: str,
        shape: str,
        x: float,
        y: float,
        width: float,
        height: float,
    ):
        """Initialize a node.

        Args:
            id: Unique identifier for the node.
            label: Text displayed in the node.
            shape: Shape of the node.
            x: X-coordinate position.
            y: Y-coordinate position.
            width: Width of the node.
            height: Height of the node.
        """
        self.id = id
        self.label = label
        self.shape = shape
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Edge:
    """Represents an edge connecting two nodes in the activity diagram.

    An edge represents a transition or flow between activities in the diagram.

    Attributes:
        id: Unique identifier for the edge.
        source: ID of the source node.
        target: ID of the target node.
        label: Optional label for the edge.
    """

    def __init__(self, id: str, source: str, target: str, label: str = ""):
        """Initialize an edge.

        Args:
            id: Unique identifier for the edge.
            source: ID of the source node.
            target: ID of the target node.
            label: Optional label for the edge.
        """
        self.id = id
        self.source = source
        self.target = target
        self.label = label


def parse_activity_diagram(content: str) -> Dict[str, List[Union[Node, Edge]]]:
    """Parse a PlantUML activity diagram into nodes and edges.

    Args:
        content: The PlantUML diagram content as a string.

    Returns:
        A dictionary containing lists of nodes and edges.
    """
    nodes: List[Node] = []
    edges: List[Edge] = []

    # Implementation would go here
    # For now, return empty lists to satisfy mypy
    return {"nodes": nodes, "edges": edges}


def layout_activitydiagram(
    nodes, edges, vertical_spacing=100, horizontal_spacing=200, start_x=60, start_y=60
):
    """
    Neues Layout für Aktivitätsdiagramme mittels rekursiver Tiefensuche (DFS) und Spaltenzuordnung.
    """
    # Konstanten für Labels und Shapes
    LABEL_START = "start"
    LABEL_STOP = "stop"
    LABEL_MERGE = "merge"
    SHAPE_HEXAGON = "hexagon"
    PATH_LABEL_NO = "nein"

    # Maximale Rekursionstiefe erhöhen für komplexe Diagramme
    sys.setrecursionlimit(max(1000, len(nodes) * 5))

    # Hilfsfunktion: Knoten-ID-Mapping erstellen
    def create_node_id_mapping():
        return {node.id: node for node in nodes}

    # Hilfsfunktion: Adjazenzlisten erstellen
    def create_adjacency_list():
        graph = defaultdict(list)
        for edge in edges:
            graph[edge.source].append((edge.target, edge.label.lower()))
        return graph

    # Rekursive DFS-Funktion mit Memoization
    def dfs(node_id, curr_col, curr_order):
        # Wenn der Knoten bereits besucht wurde, optimale Position aktualisieren
        if node_id in column_mapping:
            if node_by_id[node_id].label.lower() == LABEL_MERGE:
                # Merge-Knoten: maximalen Order verwenden (nach unten)
                order_mapping[node_id] = max(order_mapping[node_id], curr_order)
            else:
                # Andere Knoten: minimalen Order verwenden (nach oben)
                order_mapping[node_id] = min(order_mapping[node_id], curr_order)
            column_mapping[node_id] = min(column_mapping[node_id], curr_col)
            return

        # Neue Position zuweisen
        column_mapping[node_id] = curr_col
        order_mapping[node_id] = curr_order

        # Alle Kinder durchlaufen
        for index, (child_id, path_label) in enumerate(graph.get(node_id, [])):
            child_node = node_by_id.get(child_id)
            if not child_node:
                continue

            next_col, next_order = calculate_next_position(
                node_id, child_id, path_label, index, curr_col, curr_order
            )
            dfs(child_id, next_col, next_order)

    # Berechnung der nächsten Position für einen Knoten
    def calculate_next_position(
        parent_id, child_id, path_label, index, curr_col, curr_order
    ):
        child_node = node_by_id.get(child_id)

        # Merge-Knoten: gleiche Spalte, eine Ebene tiefer
        if child_node and child_node.label.lower() == LABEL_MERGE:
            return curr_col, curr_order + 1

        # Entscheidungsknoten verarbeiten
        if node_by_id[parent_id].shape == SHAPE_HEXAGON:
            if index == 0:
                # Erster Ausgang (Ja-Pfad) - gleiche Spalte, eine Ebene tiefer
                return curr_col, curr_order + 1
            else:
                # Alternative Ausgänge - neue Spalte, gleiche Ebene
                return curr_col + 1, curr_order

        # Normale Knoten: Nein-Pfad in neue Spalte, sonst eine Ebene tiefer
        if path_label == PATH_LABEL_NO:
            return curr_col + 1, curr_order
        else:
            return curr_col, curr_order + 1

    # Hilfsfunktion: Startknoten finden
    def find_start_nodes():
        start_nodes = [node for node in nodes if node.label.lower() == LABEL_START]
        if not start_nodes and nodes:
            start_nodes = [nodes[0]]  # Fallback zum ersten Knoten
        return start_nodes

    # Hilfsfunktion: Stop-Knoten ans Ende setzen
    def position_stop_nodes():
        if not order_mapping:
            return

        max_order = max(order_mapping.values())
        for node in nodes:
            if node.label.lower() == LABEL_STOP:
                order_mapping[node.id] = max_order + 1

    # Hilfsfunktion: Finale Koordinaten zuweisen
    def assign_coordinates():
        # Knoten nach Spalten gruppieren
        columns = defaultdict(list)
        for node in nodes:
            col = column_mapping.get(node.id, 1)
            columns[col].append(node)

        # Horizontaler Offset für die erste Spalte
        x_offset = 40

        # Koordinaten zuweisen
        for col, node_list in columns.items():
            # Sortieren nach Order und ID
            node_list.sort(key=lambda n: (order_mapping.get(n.id, 0), int(n.id)))
            for node in node_list:
                node.x = (
                    (start_x + x_offset)
                    + (col - 1) * horizontal_spacing
                    - node.width / 2
                )
                node.y = start_y + order_mapping.get(node.id, 0) * vertical_spacing

    # Hauptroutine
    node_by_id = create_node_id_mapping()
    graph = create_adjacency_list()
    column_mapping = {}
    order_mapping = {}

    # DFS starten
    for start_node in find_start_nodes():
        dfs(start_node.id, 1, 0)

    # Nachbearbeitung
    position_stop_nodes()
    assign_coordinates()


def is_valid_activity_diagram(content: str) -> bool:
    """Check if the content represents a valid activity diagram."""
    # Schnelle String-Überprüfungen zuerst für bessere Performance
    if "@startuml" not in content or "@enduml" not in content:
        return False

    content_lower = content.lower()
    if "start" not in content_lower or "stop" not in content_lower:
        return False

    # Überprüfung auf Aktivitätszeile oder if-Block mit kompilierten Regex-Mustern
    if not RE_ACTIVITY.search(content):
        # Wenn keine Aktivitätszeile gefunden wurde, alternativ nach einem if-Block suchen
        if not RE_IF_BLOCK.search(content):
            return False

    return True


class ActivityDiagramProcessor(BaseDiagramProcessor):
    """Processor for converting PlantUML activity diagrams to Draw.io format."""

    def is_valid_diagram(self, content: str) -> bool:
        """Check if the diagram content can be processed by this processor."""
        return is_valid_activity_diagram(content)

    def convert_to_drawio(self, content: str) -> str:
        """Convert the PlantUML activity diagram to Draw.io format."""
        # Parse the diagram
        diagram_data = parse_activity_diagram(content)

        # Basic conversion to Draw.io XML format
        xml = """
        <mxGraphModel>
            <root>
                <mxCell id="0"/>
                <mxCell id="1" parent="0"/>
        """

        # Add elements
        for node in diagram_data["nodes"]:
            style = self._get_node_style(node)
            xml += f"""
                <mxCell id="{node['id']}"
                        value="{node['label']}"
                        style="{style}"
                        vertex="1" parent="1">
                    <mxGeometry x="{node['x']}" y="{node['y']}"
                               width="{node['width']}" height="{node['height']}"
                               as="geometry"/>
                </mxCell>
            """

        # Add connections
        for edge in diagram_data["edges"]:
            xml += f"""
                <mxCell id="edge_{edge['id']}"
                        value="{edge['label']}"
                        edge="1"
                        parent="1"
                        source="{edge['source']}"
                        target="{edge['target']}"
                        style="edgeStyle=elbowEdgeStyle;elbow=vertical;strokeWidth=1.5;">
                    <mxGeometry relative="1" as="geometry"/>
                </mxCell>
            """

        xml += """
            </root>
        </mxGraphModel>
        """

        return xml

    def _get_node_style(self, node):
        """Get the style for a node based on its shape."""
        STYLES = {
            "start_stop": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;fontColor=#ffffff;",
            "ellipse": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;",
            "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontSize=12;fontColor=#ffffff;fillColor=#00A5E1;strokeColor=none;size=10;",
            "merge": "rhombus;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#00A5E1;fontColor=#ffffff;",
            "rectangle": "rounded=1;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#DCE9F1;",
        }

        if node["label"] in ["Start", "Stop"]:
            return STYLES["start_stop"]
        elif node["shape"] == "ellipse":
            return STYLES["ellipse"]
        elif node["shape"] == "hexagon":
            return STYLES["hexagon"]
        elif node["label"] == "Merge":
            return STYLES["merge"]
        else:
            return STYLES["rectangle"]


def layout_activity_diagram(
    nodes, edges, vertical_spacing=100, horizontal_spacing=200, start_x=60, start_y=60
):
    """
    Neues Layout für Aktivitätsdiagramme mittels rekursiver Tiefensuche (DFS) und Spaltenzuordnung.
    """
    # Konstanten für Labels und Shapes
    LABEL_START = "start"
    LABEL_STOP = "stop"
    LABEL_MERGE = "merge"
    SHAPE_HEXAGON = "hexagon"
    PATH_LABEL_NO = "nein"

    # Maximale Rekursionstiefe erhöhen für komplexe Diagramme
    sys.setrecursionlimit(max(1000, len(nodes) * 5))

    # Hilfsfunktion: Knoten-ID-Mapping erstellen
    def create_node_id_mapping():
        return {node.id: node for node in nodes}

    # Hilfsfunktion: Adjazenzlisten erstellen
    def create_adjacency_list():
        graph = defaultdict(list)
        for edge in edges:
            graph[edge.source].append((edge.target, edge.label.lower()))
        return graph

    # Rekursive DFS-Funktion mit Memoization
    def dfs(node_id, curr_col, curr_order):
        # Wenn der Knoten bereits besucht wurde, optimale Position aktualisieren
        if node_id in column_mapping:
            if node_by_id[node_id].label.lower() == LABEL_MERGE:
                # Merge-Knoten: maximalen Order verwenden (nach unten)
                order_mapping[node_id] = max(order_mapping[node_id], curr_order)
            else:
                # Andere Knoten: minimalen Order verwenden (nach oben)
                order_mapping[node_id] = min(order_mapping[node_id], curr_order)
            column_mapping[node_id] = min(column_mapping[node_id], curr_col)
            return

        # Neue Position zuweisen
        column_mapping[node_id] = curr_col
        order_mapping[node_id] = curr_order

        # Alle Kinder durchlaufen
        for index, (child_id, path_label) in enumerate(graph.get(node_id, [])):
            child_node = node_by_id.get(child_id)
            if not child_node:
                continue

            next_col, next_order = calculate_next_position(
                node_id, child_id, path_label, index, curr_col, curr_order
            )
            dfs(child_id, next_col, next_order)

    # Berechnung der nächsten Position für einen Knoten
    def calculate_next_position(
        parent_id, child_id, path_label, index, curr_col, curr_order
    ):
        child_node = node_by_id.get(child_id)

        # Merge-Knoten: gleiche Spalte, eine Ebene tiefer
        if child_node and child_node.label.lower() == LABEL_MERGE:
            return curr_col, curr_order + 1

        # Entscheidungsknoten verarbeiten
        if node_by_id[parent_id].shape == SHAPE_HEXAGON:
            if index == 0:
                # Erster Ausgang (Ja-Pfad) - gleiche Spalte, eine Ebene tiefer
                return curr_col, curr_order + 1
            else:
                # Alternative Ausgänge - neue Spalte, gleiche Ebene
                return curr_col + 1, curr_order

        # Normale Knoten: Nein-Pfad in neue Spalte, sonst eine Ebene tiefer
        if path_label == PATH_LABEL_NO:
            return curr_col + 1, curr_order
        else:
            return curr_col, curr_order + 1

    # Hilfsfunktion: Startknoten finden
    def find_start_nodes():
        start_nodes = [node for node in nodes if node.label.lower() == LABEL_START]
        if not start_nodes and nodes:
            start_nodes = [nodes[0]]  # Fallback zum ersten Knoten
        return start_nodes

    # Hilfsfunktion: Stop-Knoten ans Ende setzen
    def position_stop_nodes():
        if not order_mapping:
            return

        max_order = max(order_mapping.values())
        for node in nodes:
            if node.label.lower() == LABEL_STOP:
                order_mapping[node.id] = max_order + 1

    # Hilfsfunktion: Finale Koordinaten zuweisen
    def assign_coordinates():
        # Knoten nach Spalten gruppieren
        columns = defaultdict(list)
        for node in nodes:
            col = column_mapping.get(node.id, 1)
            columns[col].append(node)

        # Horizontaler Offset für die erste Spalte
        x_offset = 40

        # Koordinaten zuweisen
        for col, node_list in columns.items():
            # Sortieren nach Order und ID
            node_list.sort(key=lambda n: (order_mapping.get(n.id, 0), int(n.id)))
            for node in node_list:
                node.x = (
                    (start_x + x_offset)
                    + (col - 1) * horizontal_spacing
                    - node.width / 2
                )
                node.y = start_y + order_mapping.get(node.id, 0) * vertical_spacing

    # Hauptroutine
    node_by_id = create_node_id_mapping()
    graph = create_adjacency_list()
    column_mapping = {}
    order_mapping = {}

    # DFS starten
    for start_node in find_start_nodes():
        dfs(start_node.id, 1, 0)

    # Nachbearbeitung
    position_stop_nodes()
    assign_coordinates()


def create_activity_drawio_xml(nodes, edges):
    """
    Erstellt ein Draw.io-XML-Dokument aus den gegebenen Knoten und Kanten.
    """
    # XML-Header und Grundstruktur
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{timestamp}" agent="PlantUML2Drawio" version="14.6.13">
  <diagram id="activity_diagram" name="Activity Diagram">
    <mxGraphModel dx="1422" dy="798" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
"""

    # Knoten hinzufügen
    for node in nodes:
        style = get_node_style(node)
        xml += f"""        <mxCell id="{node.id}" value="{node.label}" style="{style}" vertex="1" parent="1">
          <mxGeometry x="{node.x}" y="{node.y}" width="{node.width}" height="{node.height}" as="geometry"/>
        </mxCell>
"""

    # Kanten hinzufügen
    for edge in edges:
        style = get_edge_style(edge)
        xml += f"""        <mxCell id="{edge.id}" value="{edge.label}" style="{style}" edge="1" parent="1" source="{edge.source}" target="{edge.target}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
"""

    # XML-Footer
    xml += """      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""

    return xml


def get_node_style(node):
    """Bestimmt den Stil eines Knotens basierend auf seinem Typ."""
    STYLES = {
        "start_stop": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;fontColor=#ffffff;",
        "ellipse": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;",
        "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontSize=12;fontColor=#ffffff;fillColor=#00A5E1;strokeColor=none;size=10;",
        "merge": "rhombus;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#00A5E1;fontColor=#ffffff;",
        "rectangle": "rounded=1;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#DCE9F1;",
    }

    if node.label in ["Start", "Stop"]:
        return STYLES["start_stop"]
    elif node.shape == "ellipse":
        return STYLES["ellipse"]
    elif node.shape == "hexagon":
        return STYLES["hexagon"]
    elif node.label == "Merge":
        return STYLES["merge"]
    else:
        return STYLES["rectangle"]


def get_edge_style(edge):
    """Bestimmt den Stil einer Kante."""
    return "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#000000;"
