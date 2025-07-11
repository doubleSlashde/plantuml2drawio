"""Activity diagram processor module for PlantUML to Draw.io conversion."""

import json
import re
import sys
import uuid
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

# Try to import from installed package or development path
try:
    # Installed package path
    from plantuml2drawio.models import Edge, Node
    from plantuml2drawio.processors.base_processor import BaseDiagramProcessor
except ImportError:
    # Development path
    from src.plantuml2drawio.models import Edge, Node
    from src.plantuml2drawio.processors.base_processor import BaseDiagramProcessor

# Predefined regex patterns for better performance
RE_ACTIVITY = re.compile(
    r":\s*(.+?);", re.DOTALL
)  # DOTALL allows newlines in activities
RE_IF_BLOCK = re.compile(r"if\s*\(.+?\).+?endif", re.DOTALL | re.IGNORECASE)
RE_START_STOP = re.compile(r"start|stop", re.IGNORECASE)


def calculate_width(node: Node) -> float:
    """Calculate the width of a node based on its label length."""
    if "\n" in node.label:
        # For multiline text, find the longest line
        lines = node.label.split("\n")
        max_length = max(len(line) for line in lines)
        return max_length * 10 + 40
    return len(node.label) * 10 + 40


def calculate_height(node: Node) -> float:
    """Calculate the height of a node."""
    if "\n" in node.label:
        # For multiline text, increase height based on number of lines
        lines = node.label.split("\n")
        return 40 + (len(lines) - 1) * 20
    return 40


def parse_activity_diagram(content: str) -> Tuple[List[Node], List[Edge]]:
    """Parse a PlantUML activity diagram into nodes and edges.

    Args:
        content: PlantUML content to parse

    Returns:
        A tuple containing:
        - nodes: List of Node objects representing the diagram elements
        - edges: List of Edge objects representing the connections
    """
    # This function is kept for backward compatibility
    # It delegates to ActivityDiagramProcessor's implementation
    processor = ActivityDiagramProcessor()
    return processor.parse_diagram(content)


def layout_activity_diagram(
    nodes: List[Node],
    edges: List[Edge],
    vertical_spacing=100,
    horizontal_spacing=200,
    start_x=60,
    start_y=60,
):
    """Calculate layout for activity diagram nodes.

    Args:
        nodes: List of Node objects to position
        edges: List of Edge objects used to determine relationships
        vertical_spacing: Vertical spacing between nodes
        horizontal_spacing: Horizontal spacing between nodes
        start_x: X-coordinate for the first node
        start_y: Y-coordinate for the first node
    """
    # This function is kept for backward compatibility
    # It delegates to ActivityDiagramProcessor's implementation
    processor = ActivityDiagramProcessor()
    processor.layout_diagram(nodes, edges)


def create_activity_drawio_xml(nodes: List[Node], edges: List[Edge]) -> str:
    """Create a Draw.io XML representation of the activity diagram.

    Args:
        nodes: List of Node objects with position information
        edges: List of Edge objects defining connections

    Returns:
        String containing the Draw.io XML representation
    """
    # This function is kept for backward compatibility
    # It delegates to ActivityDiagramProcessor's implementation
    processor = ActivityDiagramProcessor()
    return processor.export_to_drawio(nodes, edges)


def is_valid_activity_diagram(content: str) -> bool:
    """Check if the PlantUML content is a valid activity diagram.

    Args:
        content: PlantUML content to check

    Returns:
        True if the content is a valid activity diagram, False otherwise
    """
    if not content:
        return False

    # Check if @startuml and @enduml are present
    if "@startuml" not in content or "@enduml" not in content:
        return False

    content_lower = content.lower()
    if "start" not in content_lower or "stop" not in content_lower:
        return False

    # Check for activity lines or if-blocks with compiled regex patterns
    if not RE_ACTIVITY.search(content):
        # If no activity line is found, alternatively check for an if-block
        if not RE_IF_BLOCK.search(content):
            return False

    return True


class ActivityDiagramProcessor(BaseDiagramProcessor):
    """Processor for converting PlantUML activity diagrams to Draw.io format."""

    @classmethod
    def detect_diagram_type(cls, content: str) -> float:
        """Detect if the content is an activity diagram.

        Args:
            content: PlantUML content to analyze

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not content:
            return 0.0

        # Check basic requirements
        content_lower = content.lower()
        if "@startuml" not in content or "@enduml" not in content:
            return 0.0

        # Start calculating confidence score
        confidence = 0.0

        # Strong indicators
        if "start" in content_lower and "stop" in content_lower:
            confidence += 0.5

        # Activity keywords
        activity_keywords = [
            "if",
            "then",
            "else",
            "endif",
            "fork",
            "end fork",
            "split",
            "end split",
            "repeat",
            "backward",
            "while",
            "endwhile",
            "switch",
            "case",
            "endswitch",
        ]

        for keyword in activity_keywords:
            if keyword in content_lower:
                confidence += 0.1

        # Activity actions
        if RE_ACTIVITY.search(content):
            confidence += 0.3

        # If-blocks
        if RE_IF_BLOCK.search(content):
            confidence += 0.2

        # Cap at 1.0
        return min(confidence, 1.0)

    def is_valid_diagram(self, content: str) -> bool:
        """Check if the diagram content can be processed by this processor.

        Args:
            content: The diagram content to validate.

        Returns:
            True if the content can be processed, False otherwise.
        """
        return is_valid_activity_diagram(content)

    def parse_diagram(self, content: str) -> Tuple[List[Node], List[Edge]]:
        """Parse the PlantUML activity diagram content into nodes and edges.

        Args:
            content: PlantUML content to parse

        Returns:
            A tuple containing:
            - nodes: List of Node objects representing the activity diagram elements
            - edges: List of Edge objects representing the connections between elements
        """
        # Initialize collections for nodes and edges
        nodes = []
        edges = []

        # Dictionary to track node IDs by labels to ensure we connect things properly
        node_id_map = {}

        # Clean up the content: remove comments and empty lines
        lines = content.split("\n")
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("@") and not line.startswith("'"):
                clean_lines.append(line)

        # Current node ID counter starting at 10 (0 and 1 are reserved)
        next_id = 10
        last_node_id = None

        # Process start node first
        start_match = re.search(r"\bstart\b", content, re.IGNORECASE)
        if start_match:
            node_id = str(next_id)
            start_node = Node(node_id, "Start", "start_stop")
            nodes.append(start_node)
            node_id_map["start"] = node_id
            last_node_id = node_id
            next_id += 1

        # Create a stop node, but don't set connections yet
        stop_match = re.search(r"\bstop\b", content, re.IGNORECASE)
        if stop_match:
            node_id = str(next_id)
            stop_node = Node(node_id, "Stop", "start_stop")
            nodes.append(stop_node)
            node_id_map["stop"] = node_id
            next_id += 1

        # Now process lines sequentially to maintain proper order
        in_if_block = False
        if_block_content = ""
        decision_node_id = None
        branch_end_nodes = []

        for line in clean_lines:
            # Skip start/stop as they are already processed
            if re.match(r"^\s*(start|stop)\s*$", line, re.IGNORECASE):
                continue

            # If we're inside an if block, collect lines until endif
            if in_if_block:
                if_block_content += line + "\n"

                # Check if this is the end of the if block
                if re.match(r"^\s*endif\s*$", line, re.IGNORECASE):
                    in_if_block = False

                    # Process the complete if block
                    # Extract the condition text between if( and )
                    condition_match = re.search(
                        r"if\s*\((.+?)\)", if_block_content, re.DOTALL | re.IGNORECASE
                    )
                    if condition_match:
                        condition = condition_match.group(1).strip()

                        # Extract the 'then' and 'else' branches
                        then_match = re.search(
                            r"then\s*\((.*?)\)(.*?)(?:else|endif)",
                            if_block_content,
                            re.DOTALL | re.IGNORECASE,
                        )
                        else_match = re.search(
                            r"else\s*\((.*?)\)(.*?)endif",
                            if_block_content,
                            re.DOTALL | re.IGNORECASE,
                        )

                        # Process 'then' branch activities
                        if then_match:
                            then_label = then_match.group(1).strip()
                            then_content = then_match.group(2).strip()
                            then_activities = RE_ACTIVITY.finditer(then_content)

                            last_branch_node_id = decision_node_id
                            for activity_match in then_activities:
                                activity_label = activity_match.group(1).strip()
                                activity_node_id = str(next_id)
                                next_id += 1

                                activity_node = Node(
                                    activity_node_id, activity_label, "activity"
                                )
                                nodes.append(activity_node)

                                # Connect to the previous node in this branch
                                if last_branch_node_id == decision_node_id:
                                    # First node after decision gets the branch label
                                    edges.append(
                                        Edge(
                                            last_branch_node_id,
                                            activity_node_id,
                                            then_label,
                                        )
                                    )
                                else:
                                    edges.append(
                                        Edge(last_branch_node_id, activity_node_id)
                                    )

                                last_branch_node_id = activity_node_id

                            # Add last node of this branch to the collection for merge connection
                            if last_branch_node_id != decision_node_id:
                                branch_end_nodes.append(last_branch_node_id)

                        # Process 'else' branch activities
                        if else_match:
                            else_label = else_match.group(1).strip()
                            else_content = else_match.group(2).strip()
                            else_activities = RE_ACTIVITY.finditer(else_content)

                            last_branch_node_id = decision_node_id
                            for activity_match in else_activities:
                                activity_label = activity_match.group(1).strip()
                                activity_node_id = str(next_id)
                                next_id += 1

                                activity_node = Node(
                                    activity_node_id, activity_label, "activity"
                                )
                                nodes.append(activity_node)

                                # Connect to the previous node in this branch
                                if last_branch_node_id == decision_node_id:
                                    # First node after decision gets the branch label
                                    edges.append(
                                        Edge(
                                            last_branch_node_id,
                                            activity_node_id,
                                            else_label,
                                        )
                                    )
                                else:
                                    edges.append(
                                        Edge(last_branch_node_id, activity_node_id)
                                    )

                                last_branch_node_id = activity_node_id

                            # Add last node of this branch to the collection for merge connection
                            if last_branch_node_id != decision_node_id:
                                branch_end_nodes.append(last_branch_node_id)

                    # Create a merge node if we have branches to connect
                    if branch_end_nodes:
                        merge_node_id = str(next_id)
                        next_id += 1
                        merge_node = Node(merge_node_id, "", "merge")
                        nodes.append(merge_node)

                        # Connect branch end nodes to merge node
                        for branch_node_id in branch_end_nodes:
                            edges.append(Edge(branch_node_id, merge_node_id))

                        # Use merge node as the last node for connecting next elements
                        last_node_id = merge_node_id
                        branch_end_nodes = []

                    if_block_content = ""

                # Continue to next line since we're still processing the if block
                continue

            # Check if this is the start of an if block
            if_start_match = re.match(r"^\s*if\s*\(.+?\)\s*then", line, re.IGNORECASE)
            if if_start_match:
                in_if_block = True
                if_block_content = line + "\n"

                # Extract the condition
                condition_match = re.search(r"if\s*\((.+?)\)", line, re.IGNORECASE)
                condition = (
                    condition_match.group(1).strip() if condition_match else "Condition"
                )

                # Create decision node
                decision_node_id = str(next_id)
                next_id += 1
                decision_node = Node(decision_node_id, condition, "decision")
                nodes.append(decision_node)

                # Connect to previous node
                if last_node_id:
                    edges.append(Edge(last_node_id, decision_node_id))

                continue

            # Handle normal activity lines
            activity_match = RE_ACTIVITY.search(line)
            if activity_match:
                label = activity_match.group(1).strip()

                # Create activity node
                node_id = str(next_id)
                next_id += 1
                activity_node = Node(node_id, label, "activity")
                nodes.append(activity_node)

                # Connect to previous node
                if last_node_id:
                    edges.append(Edge(last_node_id, node_id))

                last_node_id = node_id

        # Connect last node to stop node if both exist and not already connected
        if (
            last_node_id
            and "stop" in node_id_map
            and last_node_id != node_id_map["stop"]
        ):
            # Check if connection already exists
            connection_exists = False
            for edge in edges:
                if edge.source == last_node_id and edge.target == node_id_map["stop"]:
                    connection_exists = True
                    break

            if not connection_exists:
                edges.append(Edge(last_node_id, node_id_map["stop"]))

        return nodes, edges

    def layout_diagram(self, nodes: List[Node], edges: List[Edge]) -> None:
        """Calculate the layout for the activity diagram elements.

        This function modifies the nodes in place by setting their x, y, width,
        and height properties based on their relationships defined by edges.

        Args:
            nodes: List of Node objects to position
            edges: List of Edge objects defining the relationships
        """
        if not nodes:
            return

        # First, set dimensions for all nodes
        for node in nodes:
            # Adjust width and height based on node type
            if node.label.lower() in ["start", "stop"] or node.type == "start_stop":
                # Smaller fixed size for start/stop nodes
                node.width = 40
                node.height = 40
            elif node.type == "activity":
                # Calculate width based on label length
                label_lines = node.label.split("\n")
                max_line_length = max(len(line) for line in label_lines)
                node.width = max(120, max_line_length * 7)  # Adjust for proper fit
                node.height = max(40, 20 + 20 * len(label_lines))
            elif node.type == "decision":
                # For decision nodes, set hexagon size
                node.width = 120
                node.height = 60
            elif node.type == "merge":
                # For merge nodes (diamond)
                node.width = 40
                node.height = 40
            else:
                # For other node types
                node.width = 120
                node.height = 60

        # Constants for layout
        start_x = 350  # Center X position
        start_y = 100  # Starting Y position
        vertical_spacing = 50  # Spacing between nodes vertically
        horizontal_spacing = 180  # Spacing between branches horizontally

        # Create adjacency lists (both incoming and outgoing)
        outgoing = defaultdict(list)
        incoming = defaultdict(list)
        for edge in edges:
            outgoing[edge.source].append((edge.target, edge.label or ""))
            incoming[edge.target].append((edge.source, edge.label or ""))

        # Find start and stop nodes
        start_node = None
        for node in nodes:
            if node.type == "start_stop" and node.label.lower() == "start":
                start_node = node
                break

        if not start_node and nodes:
            # If no explicit start node, find nodes with no incoming edges
            for node in nodes:
                if node.id not in incoming:
                    start_node = node
                    break

        if not start_node and nodes:
            # Still no start node, use the first node
            start_node = nodes[0]

        # Track visited nodes and their positions
        visited = set()

        # Create a node id to node object mapping
        node_map = {node.id: node for node in nodes}

        # Function to determine if a node is a decision node
        def is_decision(node_id):
            return node_map.get(node_id) and node_map[node_id].type == "decision"

        # Function to determine if a node is a merge node
        def is_merge(node_id):
            return node_map.get(node_id) and node_map[node_id].type == "merge"

        # Helper function for traversal to position nodes
        def position_node(node_id, x, y, branch_offset=0):
            if node_id in visited:
                return y

            visited.add(node_id)
            node = node_map[node_id]

            # Position this node
            node.x = x - node.width / 2  # Center horizontally on x
            node.y = y

            if is_decision(node_id):
                # Handle decision node (with branches)
                next_y = y + node.height + vertical_spacing

                # Collect 'then' and 'else' branches
                then_branches = []
                else_branches = []

                # Check if there are exactly two outgoing edges
                if len(outgoing[node_id]) == 2:
                    # Create a list of (target_id, label) pairs, sorted by label
                    sorted_branches = sorted(outgoing[node_id], key=lambda x: x[1])

                    # First branch is typically 'then' (to the right)
                    then_branches = [sorted_branches[0][0]]

                    # Second branch is typically 'else' (to the left)
                    else_branches = [sorted_branches[1][0]]
                else:
                    # If we have more than 2 or just 1 outgoing edge, use heuristics
                    for target, label in outgoing[node_id]:
                        # Use position in source file as a heuristic -
                        # 'then' branches tend to come first
                        if len(then_branches) <= len(else_branches):
                            then_branches.append(target)
                        else:
                            else_branches.append(target)

                # Position 'then' branches (to the right)
                then_end_y = next_y
                for branch in then_branches:
                    if branch not in visited:
                        branch_end_y = position_node(
                            branch, x + horizontal_spacing, next_y, 1
                        )
                        then_end_y = max(then_end_y, branch_end_y)

                # Position 'else' branches (to the left)
                else_end_y = next_y
                for branch in else_branches:
                    if branch not in visited:
                        branch_end_y = position_node(
                            branch, x - horizontal_spacing, next_y, -1
                        )
                        else_end_y = max(else_end_y, branch_end_y)

                # Return the maximum y reached across all branches
                max_branch_y = max(then_end_y, else_end_y)

                # Check if there's a merge node connected to this decision path
                merge_nodes = []
                for n in nodes:
                    if n.type == "merge" and n.id not in visited:
                        # Check if this merge has incoming edges from the branches
                        merge_connected_to_branches = False
                        for branch in then_branches + else_branches:
                            for child, _ in outgoing[branch]:
                                if child == n.id:
                                    merge_connected_to_branches = True
                                    break
                        if merge_connected_to_branches:
                            merge_nodes.append(n.id)

                # Position merge node after the branches
                for merge_id in merge_nodes:
                    merge_y = max_branch_y + vertical_spacing
                    position_node(merge_id, x, merge_y, branch_offset)
                    max_branch_y = (
                        merge_y + node_map[merge_id].height + vertical_spacing
                    )

                return max_branch_y
            else:
                # For regular nodes, position sequentially
                next_y = y + node.height + vertical_spacing

                # Process child nodes
                max_child_y = next_y
                for child, _ in outgoing[node_id]:
                    if child not in visited:
                        # For sequential flow, maintain x position (with minor offset for branching clarity)
                        offset_x = (
                            x + branch_offset * 10
                        )  # Subtle offset for branching clarity
                        child_end_y = position_node(
                            child, offset_x, max_child_y, branch_offset
                        )
                        max_child_y = max(max_child_y, child_end_y + vertical_spacing)

                return max_child_y

        # Start positioning from the start node
        if start_node:
            position_node(start_node.id, start_x, start_y)

        # Handle any unvisited nodes (disconnected components)
        current_y = start_y
        for node in nodes:
            if node.id not in visited:
                # Find the maximum y position among visited nodes
                if visited:
                    current_y = (
                        max(
                            [
                                node_map[node_id].y + node_map[node_id].height
                                for node_id in visited
                            ]
                        )
                        + vertical_spacing
                    )
                node.x = start_x - node.width / 2  # Center on start_x
                node.y = current_y
                current_y += node.height + vertical_spacing

        # Final pass - ensure stop node is at the bottom
        stop_nodes = [
            node
            for node in nodes
            if node.type == "start_stop" and node.label.lower() == "stop"
        ]
        if stop_nodes:
            # Find maximum y of all nodes
            max_y = max(
                [node.y + node.height for node in nodes if node.id != stop_nodes[0].id]
            )
            stop_nodes[0].y = max_y + vertical_spacing

    def export_to_drawio(self, nodes: List[Node], edges: List[Edge]) -> str:
        """Export the activity diagram to Draw.io XML format.

        Args:
            nodes: List of Node objects with position information
            edges: List of Edge objects defining connections

        Returns:
            String containing the Draw.io XML representation
        """
        if not nodes:
            return ""

        # Import html module for escaping
        import html

        # XML header
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<mxfile host="app.diagrams.net" modified="2023-01-01T00:00:00.000Z" '
            'agent="PlantUML2Drawio" version="14.6.13">\n'
            '  <diagram id="activity_diagram" name="Activity Diagram">\n'
            '    <mxGraphModel dx="1422" dy="798" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
            'pageScale="1" pageWidth="827" pageHeight="1169" math="0" '
            'shadow="0">\n'
            "      <root>\n"
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
        )

        # Add nodes to XML
        for node in nodes:
            style = self._get_node_style(node)

            # Handle multiline labels by replacing newlines with HTML line breaks
            label = node.label
            if "\n" in label:
                # First escape all XML special characters
                escaped_label = html.escape(label)
                # Then replace newlines with HTML br tag escape sequence
                label = escaped_label.replace("\n", "&lt;br&gt;")
            else:
                # Always escape the label to handle special characters
                label = html.escape(label)

            xml += (
                f'        <mxCell id="{node.id}" value="{label}" '
                f'style="{style}" vertex="1" parent="1">\n'
                f'          <mxGeometry x="{node.x}" y="{node.y}" '
                f'width="{node.width}" height="{node.height}" as="geometry"/>\n'
                "        </mxCell>\n"
            )

        # Add edges to XML with simple numeric IDs
        edge_start_id = 1000  # Start edge IDs from 1000 to avoid conflicts
        for i, edge in enumerate(edges):
            style = self._get_edge_style(edge)

            # Handle edge labels (which could be None)
            label = edge.label or ""
            if "\n" in label:
                # First escape all XML special characters
                escaped_label = html.escape(label)
                # Then replace newlines with HTML br tag escape sequence
                label = escaped_label.replace("\n", "&lt;br&gt;")
            else:
                # Always escape the label to handle special characters
                label = html.escape(label)

            # Create a numeric edge ID
            edge_id = str(edge_start_id + i)

            xml += (
                f'        <mxCell id="{edge_id}" value="{label}" '
                f'style="{style}" edge="1" parent="1" source="{edge.source}" '
                f'target="{edge.target}">\n'
                '          <mxGeometry relative="1" as="geometry"/>\n'
                "        </mxCell>\n"
            )

        # XML footer
        xml += """      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""

        return xml

    def _get_node_style(self, node: Node) -> str:
        """Get the Draw.io style for a node based on its type.

        Args:
            node: The node to get the style for.

        Returns:
            The Draw.io style string for the node.
        """
        STYLES = {
            "start_stop": (
                "ellipse;whiteSpace=wrap;html=1;aspect=fixed;"
                "fillColor=#000000;fontColor=#ffffff;strokeColor=none;"
            ),
            "activity": (
                "rounded=1;whiteSpace=wrap;html=1;"
                "fillColor=#D7E9F4;strokeColor=none;"
            ),
            "decision": (
                "shape=hexagon;perimeter=hexagonPerimeter2;size=0.05;whiteSpace=wrap;html=1;"
                "fillColor=#00A5E1;fontColor=#FFFFFF;strokeColor=none;"
            ),
            "merge": (
                "rhombus;whiteSpace=wrap;html=1;"
                "fillColor=#00A5E1;fontColor=#FFFFFF;strokeColor=none;"
            ),
        }

        if node.label.lower() in ["start", "stop"]:
            # Set the width and height directly for start/stop nodes
            node.width = 40
            node.height = 40
            return STYLES["start_stop"]
        elif node.type == "decision":
            return STYLES["decision"]
        elif node.type == "merge":
            return STYLES["merge"]
        else:
            return STYLES["activity"]

    def _get_edge_style(self, edge: Edge) -> str:
        """Get the Draw.io style for an edge.

        Args:
            edge: The edge to get the style for.

        Returns:
            The Draw.io style string for the edge.
        """
        return (
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
            "jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#000000;"
        )

    def convert_to_drawio(self, content: str) -> str:
        """Convert the PlantUML activity diagram to Draw.io format.

        Args:
            content: The PlantUML diagram content to convert.

        Returns:
            The diagram converted to Draw.io XML format.
        """
        # Parse the diagram
        nodes, edges = self.parse_diagram(content)

        # Layout the diagram
        self.layout_diagram(nodes, edges)

        # Create the Draw.io XML
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

        # Create the JSON representation
        diagram_data = {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type,
                    "x": node.x,
                    "y": node.y,
                    "width": node.width,
                    "height": node.height,
                }
                for node in nodes
            ],
            "edges": [
                {
                    "id": f"edge_{edge.source}_{edge.target}",
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.label,
                }
                for edge in edges
            ],
        }

        return json.dumps(diagram_data, indent=2)
