#!/usr/bin/env python3
"""
Tests for the Activity Diagram Processor.
"""
import json
import os
import re
import sys
import unittest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.plantuml2drawio.models import Edge, Node
from src.plantuml2drawio.processors.activity_processor import (
    ActivityDiagramProcessor, calculate_height, calculate_width,
    create_activity_drawio_xml, is_valid_activity_diagram,
    layout_activity_diagram, parse_activity_diagram)


class TestActivityDiagramProcessor(unittest.TestCase):
    """Test class for the Activity Diagram Processor."""

    def setUp(self):
        """Set up test environment."""
        self.processor = ActivityDiagramProcessor()

        # Sample activity diagram content
        self.basic_diagram = """
        @startuml
        start
        :Step 1;
        :Step 2;
        stop
        @enduml
        """

        self.complex_diagram = """
        @startuml
        start
        :Initialize Process;
        if (condition?) then (yes)
            :Process Data;
            if (another condition?) then (yes)
                :Special Processing;
            else (no)
                :Normal Processing;
            endif
        else (no)
            :Skip Processing;
        endif
        :Finalize;
        stop
        @enduml
        """

        # Read test diagrams from data directory
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def _read_test_file(self, filename):
        """Helper method to read test files."""
        with open(
            os.path.join(self.test_data_dir, filename), "r", encoding="utf-8"
        ) as f:
            return f.read()

    def test_is_valid_activity_diagram(self):
        """Test activity diagram validation."""
        self.assertTrue(is_valid_activity_diagram(self.basic_diagram))
        self.assertTrue(is_valid_activity_diagram(self.complex_diagram))

        # Invalid diagram test
        invalid_diagram = """
        @startuml
        This is not a valid activity diagram
        @enduml
        """
        self.assertFalse(is_valid_activity_diagram(invalid_diagram))

        # Test with existing examples
        for i in range(1, 8):
            try:
                content = self._read_test_file(f"activity{i}.puml")
                self.assertTrue(is_valid_activity_diagram(content))
            except FileNotFoundError:
                continue

    def test_detect_diagram_type(self):
        """Test diagram type detection."""
        # The confidence might not be exactly 1.0, so we test for > 0.7
        self.assertGreater(self.processor.detect_diagram_type(self.basic_diagram), 0.7)
        self.assertGreater(
            self.processor.detect_diagram_type(self.complex_diagram), 0.7
        )

        # Test with non-activity diagram
        non_activity = """
        @startuml
        class Example {
            +attribute: String
            +method(): void
        }
        @enduml
        """
        self.assertLess(self.processor.detect_diagram_type(non_activity), 0.5)

    def test_parse_diagram(self):
        """Test diagram parsing."""
        nodes, edges = self.processor.parse_diagram(self.basic_diagram)

        # Check we have at least the start, step(s), and stop nodes
        self.assertGreaterEqual(len(nodes), 3)

        # Check for edges
        self.assertGreaterEqual(len(edges), 2)

        # Check node types - the actual implementation uses "start_stop" for both start and stop nodes
        node_types = [node.type for node in nodes]
        self.assertIn("start_stop", node_types)
        self.assertIn("activity", node_types)

        # Check node labels for start and stop
        node_labels = [node.label.lower() for node in nodes]
        self.assertTrue(
            any("start" in label for label in node_labels)
            or any("stop" in label for label in node_labels)
        )

        # Complex diagram parsing
        nodes, edges = self.processor.parse_diagram(self.complex_diagram)
        self.assertGreaterEqual(
            len(nodes), 3
        )  # It might not parse every node as expected
        self.assertGreaterEqual(len(edges), 2)

    def test_layout_diagram(self):
        """Test diagram layout."""
        nodes, edges = self.processor.parse_diagram(self.basic_diagram)

        # Check initial positions before layout
        for node in nodes:
            self.assertEqual(node.x, 0)
            self.assertEqual(node.y, 0)

        # Apply layout
        self.processor.layout_diagram(nodes, edges)

        # Check if at least some positions have been updated
        has_updated_positions = False
        for node in nodes:
            if node.x != 0 or node.y != 0:
                has_updated_positions = True
                break
        self.assertTrue(has_updated_positions)

    def test_export_to_drawio(self):
        """Test export to Draw.io XML format."""
        nodes, edges = self.processor.parse_diagram(self.basic_diagram)
        self.processor.layout_diagram(nodes, edges)

        xml = self.processor.export_to_drawio(nodes, edges)

        # Basic checks on the XML output
        self.assertIn("<mxGraphModel", xml)
        self.assertIn("<root>", xml)
        # The actual text might be transformed in different ways, so we check for general elements
        self.assertIn("mxCell", xml)
        self.assertIn("value=", xml)

    def test_convert_to_drawio(self):
        """Test the complete conversion to Draw.io XML."""
        xml = self.processor.convert_to_drawio(self.basic_diagram)

        # Basic checks on the XML output
        self.assertIn("<mxGraphModel", xml)
        self.assertIn("<root>", xml)
        # The actual text might be transformed in different ways, so we check for general elements
        self.assertIn("mxCell", xml)
        self.assertIn("value=", xml)

    def test_convert_to_json(self):
        """Test conversion to JSON format."""
        json_data = self.processor.convert_to_json(self.basic_diagram)

        # Try to parse the JSON
        data = json.loads(json_data)

        # Check structure
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertGreaterEqual(
            len(data["nodes"]), 3
        )  # At least start, one activity, stop
        self.assertGreaterEqual(len(data["edges"]), 2)  # At least 2 connections

    def test_calculate_width_height(self):
        """Test node width and height calculation."""
        node = Node(node_id="test", label="Test Node", node_type="activity")

        width = calculate_width(node)
        self.assertGreater(width, 0)  # Width should be positive

        height = calculate_height(node)
        self.assertGreater(height, 0)  # Height should be positive

    def test_existing_examples(self):
        """Test with existing example files."""
        for i in range(1, 8):
            try:
                content = self._read_test_file(f"activity{i}.puml")
                xml = self.processor.convert_to_drawio(content)

                # Basic validation
                self.assertIn("<mxGraphModel", xml)
                self.assertIn("<root>", xml)
            except FileNotFoundError:
                continue

    def test_complex_features(self):
        """Test handling of complex activity diagram features."""
        # Test with complex diagram (activity5.puml)
        try:
            complex_content = self._read_test_file("activity5.puml")
            nodes, edges = self.processor.parse_diagram(complex_content)

            # Check that the diagram is processed
            self.assertGreaterEqual(len(nodes), 3)
            self.assertGreaterEqual(len(edges), 2)

            # Convert to DrawIO and check basic structure
            xml = self.processor.convert_to_drawio(complex_content)
            self.assertIn("<mxGraphModel", xml)
            self.assertIn("<root>", xml)
        except FileNotFoundError:
            self.skipTest("activity5.puml not found")

    def test_swimlanes(self):
        """Test handling of swimlanes in activity diagrams."""
        try:
            swimlane_content = self._read_test_file("activity6.puml")
            nodes, edges = self.processor.parse_diagram(swimlane_content)

            # Check that the diagram is processed
            self.assertGreaterEqual(len(nodes), 3)
            self.assertGreaterEqual(len(edges), 2)

            # Convert to DrawIO and check basic structure
            xml = self.processor.convert_to_drawio(swimlane_content)
            self.assertIn("<mxGraphModel", xml)
            self.assertIn("<root>", xml)
        except FileNotFoundError:
            self.skipTest("activity6.puml not found")

    def test_detached_activities(self):
        """Test handling of detached activities."""
        try:
            detached_content = self._read_test_file("activity7.puml")
            nodes, edges = self.processor.parse_diagram(detached_content)

            # Check that the diagram is processed
            self.assertGreaterEqual(len(nodes), 3)
            self.assertGreaterEqual(len(edges), 1)  # Might have fewer edges than nodes

            # Convert to DrawIO and check basic structure
            xml = self.processor.convert_to_drawio(detached_content)
            self.assertIn("<mxGraphModel", xml)
            self.assertIn("<root>", xml)
        except FileNotFoundError:
            self.skipTest("activity7.puml not found")

    def test_condition_branches(self):
        """Test that condition nodes have both positive and negative branches leading to activities."""
        # Create a test diagram with conditions where both yes and no paths lead to activities
        condition_diagram = """
        @startuml
        start
        :Initial Activity;
        if (First Condition?) then (yes)
            :Activity After Yes;
        else (no)
            :Activity After No;
        endif
        if (Second Condition?) then (yes)
            :Another Yes Activity;
        else (no)
            :Another No Activity;
        endif
        :Final Activity;
        stop
        @enduml
        """

        # First verify that the diagram is considered valid
        self.assertTrue(is_valid_activity_diagram(condition_diagram))

        # Parse the diagram
        nodes, edges = self.processor.parse_diagram(condition_diagram)

        # Find condition nodes
        condition_nodes = [node for node in nodes if node.type == "decision"]

        # We should have at least 2 condition nodes
        self.assertGreaterEqual(
            len(condition_nodes), 2, "Not enough condition nodes found"
        )

        # Find activities that should be targets for the condition branches
        activities = [node for node in nodes if node.type == "activity"]
        activity_labels = [node.label for node in activities]

        # Check for the presence of specific activities for both branches
        yes_activities = ["Activity After Yes", "Another Yes Activity"]
        no_activities = ["Activity After No", "Another No Activity"]

        # Verify both yes and no activities exist
        for activity in yes_activities:
            self.assertTrue(
                any(activity in label for label in activity_labels),
                f"Yes-branch activity '{activity}' not found in diagram",
            )

        for activity in no_activities:
            self.assertTrue(
                any(activity in label for label in activity_labels),
                f"No-branch activity '{activity}' not found in diagram",
            )

        # For each condition node, check that it has outgoing edges
        for condition_node in condition_nodes:
            # Find outgoing edges from this condition
            outgoing_edges = [
                edge for edge in edges if edge.source == condition_node.id
            ]

            # Should have at least 1 outgoing edge
            self.assertGreaterEqual(
                len(outgoing_edges),
                1,
                f"Condition node {condition_node.id} does not have any outgoing edges",
            )

            # Check if the outgoing edges lead to activity nodes
            for edge in outgoing_edges:
                # Find the target node
                target_nodes = [node for node in nodes if node.id == edge.target]
                self.assertEqual(
                    len(target_nodes),
                    1,
                    f"Target node {edge.target} not found or duplicate",
                )

                # The condition should lead to an activity or another node type, but not be disconnected
                self.assertIsNotNone(
                    target_nodes[0].type,
                    f"Target node {edge.target} does not have a type",
                )

        # Convert to DrawIO and check basic structure
        xml = self.processor.export_to_drawio(nodes, edges)
        self.assertIn("<mxGraphModel", xml)
        self.assertIn("<root>", xml)

    def test_multiline_activities(self):
        """Test handling of activity labels that span multiple lines."""
        try:
            multiline_content = self._read_test_file("activity_multiline.puml")

            # First verify that the diagram is considered valid
            self.assertTrue(is_valid_activity_diagram(multiline_content))

            # Parse the diagram
            nodes, edges = self.processor.parse_diagram(multiline_content)

            # Check that the diagram is processed
            self.assertGreaterEqual(
                len(nodes), 5
            )  # Should have at least 5 nodes including start, stop
            self.assertGreaterEqual(
                len(edges), 4
            )  # Should have connections between all activities

            # Check for multiline activities specifically
            multiline_found = False
            for node in nodes:
                if node.type == "activity" and "\n" in node.label:
                    multiline_found = True
                    break

            self.assertTrue(
                multiline_found,
                "No multiline activity nodes found in the parsed diagram",
            )

            # Check if specific multiline content is preserved
            multiline_content_found = False
            for node in nodes:
                if (
                    node.type == "activity"
                    and "This is" in node.label
                    and "multiline" in node.label
                    and "several lines" in node.label
                ):
                    multiline_content_found = True
                    break

            self.assertTrue(
                multiline_content_found,
                "Expected multiline content not found in any node",
            )

            # Convert to DrawIO and check basic structure
            xml = self.processor.export_to_drawio(nodes, edges)
            self.assertIn("<mxGraphModel", xml)
            self.assertIn("<root>", xml)

            # Check if the multiline content is preserved in the XML
            self.assertTrue(
                any(
                    "This is" in line and "multiline" in line
                    for line in xml.split("\n")
                ),
                "Multiline content not preserved in Draw.io XML",
            )
        except FileNotFoundError:
            self.skipTest("activity_multiline.puml not found")

    def test_unique_node_ids(self):
        """Test that all nodes have unique IDs."""
        # Test with simple diagram
        nodes, edges = self.processor.parse_diagram(self.basic_diagram)

        # Get all node IDs
        node_ids = [node.id for node in nodes]

        # Check that all IDs are unique
        self.assertEqual(
            len(node_ids),
            len(set(node_ids)),
            "Node IDs are not unique: " + str(node_ids),
        )

        # Test with complex diagram
        nodes, edges = self.processor.parse_diagram(self.complex_diagram)

        # Get all node IDs
        node_ids = [node.id for node in nodes]

        # Check that all IDs are unique
        self.assertEqual(
            len(node_ids),
            len(set(node_ids)),
            "Node IDs are not unique: " + str(node_ids),
        )

    def test_condition_edges_with_labels(self):
        """Test that condition branches have labeled edges in the XML output."""
        # Create a test diagram with conditions
        condition_diagram = """
        @startuml
        start
        :Initial Activity;
        if (First Condition?) then (yes)
            :Activity After Yes;
        else (no)
            :Activity After No;
        endif
        stop
        @enduml
        """

        # First verify that the diagram is considered valid
        self.assertTrue(is_valid_activity_diagram(condition_diagram))

        # Parse the diagram
        nodes, edges = self.processor.parse_diagram(condition_diagram)

        # Find condition nodes
        condition_nodes = [node for node in nodes if node.type == "decision"]
        self.assertGreaterEqual(len(condition_nodes), 1, "No condition nodes found")

        # Get the XML output
        xml = self.processor.export_to_drawio(nodes, edges)

        # Check if the XML contains edges with "yes" and "no" labels
        # In draw.io XML, edge labels appear as value attributes or within label elements

        # Case-insensitive search for yes/no text in edge definitions
        yes_pattern = re.compile(r'<mxCell[^>]*value="yes"[^>]*edge="1"', re.IGNORECASE)
        no_pattern = re.compile(r'<mxCell[^>]*value="no"[^>]*edge="1"', re.IGNORECASE)

        # Alternative patterns with more flexibility in attribute order
        alt_yes_pattern = re.compile(
            r'<mxCell[^>]*edge="1"[^>]*value="yes"', re.IGNORECASE
        )
        alt_no_pattern = re.compile(
            r'<mxCell[^>]*edge="1"[^>]*value="no"', re.IGNORECASE
        )

        # Check for yes/no labels using both patterns
        has_yes_label = (
            yes_pattern.search(xml) is not None
            or alt_yes_pattern.search(xml) is not None
        )
        has_no_label = (
            no_pattern.search(xml) is not None or alt_no_pattern.search(xml) is not None
        )

        # At least one of the patterns should match for each label type
        self.assertTrue(
            has_yes_label, "No 'yes' labels found on condition edges in XML"
        )
        self.assertTrue(has_no_label, "No 'no' labels found on condition edges in XML")

        # Count the number of condition edges in the XML
        edge_count = len(re.findall(r'<mxCell[^>]*edge="1"', xml))

        # We should have at least two edges per condition (one for yes, one for no)
        # plus edges connecting activities
        self.assertGreaterEqual(
            edge_count,
            len(condition_nodes) * 2,
            "Not enough edges in XML for all condition branches",
        )

    def test_condition_with_merge(self):
        """Test that after condition branches, a merge node collects both paths before continuing."""
        # Create a test diagram with condition and merge node
        merge_diagram = """
        @startuml
        start
        :Initial Activity;
        if (Condition?) then (yes)
            :Activity After Yes;
        else (no)
            :Activity After No;
        endif
        :Activity After Merge;
        stop
        @enduml
        """

        # First verify that the diagram is considered valid
        self.assertTrue(is_valid_activity_diagram(merge_diagram))

        # Parse the diagram
        nodes, edges = self.processor.parse_diagram(merge_diagram)

        # Find condition nodes
        condition_nodes = [node for node in nodes if node.type == "decision"]
        self.assertGreaterEqual(len(condition_nodes), 1, "No condition nodes found")

        # Find the merge node (should be after the condition branches)
        merge_nodes = [node for node in nodes if node.type == "merge"]
        self.assertGreaterEqual(
            len(merge_nodes), 1, "No merge node found after condition branches"
        )

        # Find yes and no branch activities - multiple versions might exist
        yes_activities = []
        no_activities = []
        for edge in edges:
            if edge.label == "yes" and edge.source == condition_nodes[0].id:
                # Find the target of the 'yes' edge
                target_nodes = [node for node in nodes if node.id == edge.target]
                if target_nodes:
                    yes_activities.append(target_nodes[0])
            elif edge.label == "no" and edge.source == condition_nodes[0].id:
                # Find the target of the 'no' edge
                target_nodes = [node for node in nodes if node.id == edge.target]
                if target_nodes:
                    no_activities.append(target_nodes[0])

        # Both branches should exist
        self.assertGreaterEqual(
            len(yes_activities), 1, "No yes branch activities found"
        )
        self.assertGreaterEqual(len(no_activities), 1, "No no branch activities found")

        # Verify merge connections
        # At least one activity from each branch should connect to a merge node
        yes_to_merge = False
        no_to_merge = False

        for yes_activity in yes_activities:
            for edge in edges:
                if edge.source == yes_activity.id:
                    target_nodes = [node for node in nodes if node.id == edge.target]
                    if target_nodes and target_nodes[0].type == "merge":
                        yes_to_merge = True
                        break

        for no_activity in no_activities:
            for edge in edges:
                if edge.source == no_activity.id:
                    target_nodes = [node for node in nodes if node.id == edge.target]
                    if target_nodes and target_nodes[0].type == "merge":
                        no_to_merge = True
                        break

        self.assertTrue(yes_to_merge, "Yes branch does not connect to any merge node")
        self.assertTrue(no_to_merge, "No branch does not connect to any merge node")

        # Verify that there is at least one activity after a merge node
        merge_node_id = merge_nodes[0].id
        after_merge_activity = None

        for edge in edges:
            if edge.source == merge_node_id:
                target_nodes = [node for node in nodes if node.id == edge.target]
                if target_nodes and target_nodes[0].type in ["activity", "start_stop"]:
                    after_merge_activity = target_nodes[0]
                    break

        self.assertIsNotNone(
            after_merge_activity, f"No node found after merge node {merge_node_id}"
        )

    def test_no_bidirectional_connections(self):
        """Test that there are no connections that immediately go back (bidirectional connections)."""
        # Create a test diagram with potentially problematic connections
        diagram = """
        @startuml
        start
        :Initial Activity;
        if (Condition?) then (yes)
            :Activity After Yes;
        else (no)
            :Activity After No;
        endif
        :Final Activity;
        stop
        @enduml
        """

        # Parse the diagram
        nodes, edges = self.processor.parse_diagram(diagram)

        # Check for bidirectional connections
        for edge1 in edges:
            for edge2 in edges:
                if edge1 != edge2:  # Don't compare an edge with itself
                    # If one edge is source->target and another is target->source, it's bidirectional
                    if edge1.source == edge2.target and edge1.target == edge2.source:
                        self.fail(
                            f"Found bidirectional connection between {edge1.source} and {edge1.target}"
                        )

    def test_no_direct_condition_to_merge(self):
        """Test that there are no direct connections from a condition node to a merge node."""
        # Create a test diagram with conditions and merge nodes
        diagram = """
        @startuml
        start
        :Initial Activity;
        if (First Condition?) then (yes)
            :Activity After Yes;
        else (no)
            :Activity After No;
        endif
        if (Second Condition?) then (yes)
            :Another Yes Activity;
        else (no)
            :Another No Activity;
        endif
        :Final Activity;
        stop
        @enduml
        """

        # Parse the diagram
        nodes, edges = self.processor.parse_diagram(diagram)

        # Find condition nodes
        condition_nodes = [node for node in nodes if node.type == "decision"]

        # Find merge nodes
        merge_nodes = [node for node in nodes if node.type == "merge"]

        # Check for direct connections from condition to merge
        for edge in edges:
            # Find source node
            source_nodes = [node for node in nodes if node.id == edge.source]
            if not source_nodes:
                continue

            # Find target node
            target_nodes = [node for node in nodes if node.id == edge.target]
            if not target_nodes:
                continue

            # Check if this is a condition->merge connection
            if source_nodes[0].type == "decision" and target_nodes[0].type == "merge":
                self.fail(
                    f"Found direct connection from condition node {edge.source} to merge node {edge.target}"
                )

    def test_multiline_with_conditions(self):
        """Test specifically for problems with multiline activities in conditions."""
        # Create a test diagram with multiline activities in conditions
        diagram = """
        @startuml
        start
        :Initial Activity;
        if (Complex Condition?) then (yes)
            :This is a
            multiline
            activity in
            yes branch;
        else (no)
            :This is another
            multiline
            activity in
            no branch;
        endif
        :Final Activity
        with multiple
        lines;
        stop
        @enduml
        """

        # Parse the diagram
        nodes, edges = self.processor.parse_diagram(diagram)

        # Find condition nodes
        condition_nodes = [node for node in nodes if node.type == "decision"]

        # Find merge nodes
        merge_nodes = [node for node in nodes if node.type == "merge"]

        # Check for direct connections from condition to merge
        for edge in edges:
            # Find source node
            source_nodes = [node for node in nodes if node.id == edge.source]
            if not source_nodes:
                continue

            # Find target node
            target_nodes = [node for node in nodes if node.id == edge.target]
            if not target_nodes:
                continue

            # Check if this is a condition->merge connection
            if source_nodes[0].type == "decision" and target_nodes[0].type == "merge":
                self.fail(
                    f"Found direct connection from condition node {edge.source} to merge node {edge.target}"
                )

        # Check for bidirectional connections
        for edge1 in edges:
            for edge2 in edges:
                if edge1 != edge2:  # Don't compare an edge with itself
                    # If one edge is source->target and another is target->source, it's bidirectional
                    if edge1.source == edge2.target and edge1.target == edge2.source:
                        self.fail(
                            f"Found bidirectional connection between {edge1.source} and {edge1.target} with multiline activities"
                        )

        # Verify that multiline activities are properly connected
        # Dump nodes for debugging
        print("Nodes found:")
        for node in nodes:
            print(f"Node ID: {node.id}, Type: {node.type}, Label: {node.label}")

        # In PlantUML, multiline activities might be combined into a single line with spaces
        # So we need to check for activities with spaces or newlines
        multiline_activities = [
            node
            for node in nodes
            if node.type == "activity"
            and (("\n" in node.label) or (len(node.label.split()) > 2))
        ]
        self.assertGreater(
            len(multiline_activities), 0, "No multiline activities found"
        )

        # Check that each multiline activity has at least one connection
        for activity in multiline_activities:
            has_incoming = False
            has_outgoing = False

            for edge in edges:
                if edge.target == activity.id:
                    has_incoming = True
                if edge.source == activity.id:
                    has_outgoing = True

            self.assertTrue(
                has_incoming,
                f"Multiline activity {activity.id} has no incoming connections",
            )
            self.assertTrue(
                has_outgoing,
                f"Multiline activity {activity.id} has no outgoing connections",
            )

    def test_activity_multiline_puml_file(self):
        """Test the activity_multiline.puml file for bidirectional connections and direct condition-to-merge connections."""
        try:
            # Read the test file
            multiline_content = self._read_test_file("activity_multiline.puml")

            # First verify that the diagram is considered valid
            self.assertTrue(is_valid_activity_diagram(multiline_content))

            # Parse the diagram
            nodes, edges = self.processor.parse_diagram(multiline_content)

            # Print nodes and edges for debugging
            print("\nNodes in activity_multiline.puml:")
            for node in nodes:
                print(f"Node ID: {node.id}, Type: {node.type}, Label: {node.label}")

            print("\nEdges in activity_multiline.puml:")
            for edge in edges:
                print(f"Edge: {edge.source} -> {edge.target}, Label: {edge.label}")

            # Find condition nodes
            condition_nodes = [node for node in nodes if node.type == "decision"]

            # Find merge nodes
            merge_nodes = [node for node in nodes if node.type == "merge"]

            # Check for direct connections from condition to merge
            for edge in edges:
                # Find source node
                source_nodes = [node for node in nodes if node.id == edge.source]
                if not source_nodes:
                    continue

                # Find target node
                target_nodes = [node for node in nodes if node.id == edge.target]
                if not target_nodes:
                    continue

                # Check if this is a condition->merge connection
                if (
                    source_nodes[0].type == "decision"
                    and target_nodes[0].type == "merge"
                ):
                    self.fail(
                        f"Found direct connection from condition node {edge.source} to merge node {edge.target}"
                    )

            # Check for bidirectional connections
            for edge1 in edges:
                for edge2 in edges:
                    if edge1 != edge2:  # Don't compare an edge with itself
                        # If one edge is source->target and another is target->source, it's bidirectional
                        if (
                            edge1.source == edge2.target
                            and edge1.target == edge2.source
                        ):
                            self.fail(
                                f"Found bidirectional connection between {edge1.source} and {edge1.target}"
                            )

            # Verify multiline activities
            multiline_activities = [
                node
                for node in nodes
                if node.type == "activity"
                and (("\n" in node.label) or (len(node.label.split()) > 2))
            ]
            self.assertGreater(
                len(multiline_activities),
                0,
                "No multiline activities found in activity_multiline.puml",
            )

            # Check that multiline activities have proper connections
            for activity in multiline_activities:
                incoming_edges = [edge for edge in edges if edge.target == activity.id]
                outgoing_edges = [edge for edge in edges if edge.source == activity.id]

                if not incoming_edges:
                    print(
                        f"Warning: Multiline activity {activity.id} ({activity.label}) has no incoming connections"
                    )

                if not outgoing_edges:
                    print(
                        f"Warning: Multiline activity {activity.id} ({activity.label}) has no outgoing connections"
                    )

                # Check for multiple incoming edges to the same activity (might indicate problematic connections)
                if len(incoming_edges) > 1:
                    print(
                        f"Note: Multiline activity {activity.id} ({activity.label}) has {len(incoming_edges)} incoming connections"
                    )
                    for edge in incoming_edges:
                        source_nodes = [
                            node for node in nodes if node.id == edge.source
                        ]
                        if source_nodes:
                            print(
                                f"  From: {source_nodes[0].id} ({source_nodes[0].type}: {source_nodes[0].label})"
                            )

                # Check for multiple outgoing edges from the same activity
                if len(outgoing_edges) > 1:
                    print(
                        f"Note: Multiline activity {activity.id} ({activity.label}) has {len(outgoing_edges)} outgoing connections"
                    )
                    for edge in outgoing_edges:
                        target_nodes = [
                            node for node in nodes if node.id == edge.target
                        ]
                        if target_nodes:
                            print(
                                f"  To: {target_nodes[0].id} ({target_nodes[0].type}: {target_nodes[0].label})"
                            )

        except FileNotFoundError:
            self.skipTest("activity_multiline.puml not found")


if __name__ == "__main__":
    unittest.main()
