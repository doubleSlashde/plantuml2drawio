#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
import argparse
import os

# Klassen zur Repräsentation von Knoten und Kanten im Diagramm
class Node:
    def __init__(self, id, label, shape, x, y, width, height):
        self.id = id
        self.label = label
        self.shape = shape  # z.B. "ellipse", "rectangle", "rhombus", "hexagon"
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Edge:
    def __init__(self, id, source, target, label=""):
        self.id = id
        self.source = source
        self.target = target
        self.label = label

def parse_plantuml_activity(plantuml_content):
    """
    Parst eine vereinfachte Version eines PlantUML-Aktivitätsdiagramms.
    Unterstützte Elemente:
      - start und stop
      - Aktivitäten in Form von :Text;
      - if (Bedingung) then (ja)
      - else (alternativer Text)
      - endif
      
    Besonderheiten:
      - Bei einem if wird ein Entscheidungs-Knoten erstellt, dessen ausgehender Pfeil mit dem "ja"-Text beschriftet wird.
      - Der else-Zweig erhält die alternative Beschriftung.
      - Am Ende eines if-Blocks (bei endif) wird, wenn ein else existiert, ein Merge-Knoten erstellt, der beide Zweige zusammenführt.
      - Befindet sich eine Aktivität (oder ein Zweig) am Ende ohne Folgeknoten, wird automatisch ein Pfeil zum Stop-Knoten erstellt.
      - Neu: Die erste Aktivität in beiden Zweigen wird auf einer gemeinsamen Baseline ausgerichtet.
    """
    import re

    # Prekompilierte Regex-Pattern zur Verbesserung der Performance und Lesbarkeit
    re_if = re.compile(r"if\s*\((.+)\)\s*then\s*\((.+)\)", re.IGNORECASE)
    re_else = re.compile(r"else\s*\((.+)\)", re.IGNORECASE)
    re_activity = re.compile(r":(.+);")

    # Aufteilen der Eingabe in Zeilen
    lines = plantuml_content.splitlines()
    nodes = []
    edges = []
    last_node_id = None
    node_counter = 2  # Die IDs "0" und "1" sind durch draw.io vorbelegt.
    edge_counter = 1

    # Stack für verschachtelte if-Blöcke (ohne Koordinatenverwaltung)
    pending_ifs = []

    def create_node(label, shape, x, y, width, height):
        nonlocal node_counter
        node = Node(id=str(node_counter), label=label, shape=shape,
                    x=x, y=y, width=width, height=height)
        nodes.append(node)
        node_counter += 1
        return node

    def add_edge(source, target, label=""):
        nonlocal edge_counter
        edge = Edge(id=str(edge_counter), source=source, target=target, label=label)
        edges.append(edge)
        edge_counter += 1

    # Verarbeitung der einzelnen Zeilen
    for line in lines:
        line = line.strip()
        # Kommentare, leere Zeilen und Diagramm-Markierungen überspringen
        if not line or line.startswith("'") or line.startswith("//") or \
           line.startswith("@startuml") or line.startswith("@enduml"):
            continue

        lower_line = line.lower()

        # Verarbeitung von Start und Stop
        if lower_line == "start":
            node = create_node("Start", "ellipse", 0, 0, 40, 40)
            if last_node_id is not None:
                add_edge(last_node_id, node.id)
            last_node_id = node.id
            continue

        if lower_line == "stop":
            node = create_node("Stop", "ellipse", 0, 0, 40, 40)
            if last_node_id is not None:
                add_edge(last_node_id, node.id)
            last_node_id = node.id
            continue

        # Verarbeitung der if-Bedingung
        m = re_if.match(line)
        if m:
            condition, true_label = m.group(1).strip(), m.group(2).strip()
            node = create_node(condition, "hexagon", 0, 0, 80, 40)
            if last_node_id is not None:
                add_edge(last_node_id, node.id)
            last_node_id = node.id
            pending_ifs.append({
                "decision": node.id,
                "true_label": true_label,
                "true_last": None,   # Letzter Knoten des wahren Zweigs
                "false_label": None,  # Beschriftung, falls ein else erstellt wird
                "false_last": None,   # Letzter Knoten des falschen Zweigs
                "in_false": False     # Gibt an, welcher Zweig aktiv ist
            })
            continue

        # Verarbeitung des else-Zweigs
        m = re_else.match(line)
        if m and pending_ifs:
            pending_ifs[-1]["false_label"] = m.group(1).strip()
            pending_ifs[-1]["in_false"] = True
            continue

        # Verarbeitung des endif-Schlusses
        if lower_line.startswith("endif"):
            if pending_ifs:
                current_if = pending_ifs.pop()
                if current_if["false_label"] is not None:
                    # Falls ein else-Zweig existiert, wird ein Merge-Knoten erstellt.
                    merge_node = create_node("Merge", "rhombus", 0, 0, 50, 50)
                    if current_if["true_last"] is not None:
                        add_edge(current_if["true_last"], merge_node.id)
                    if current_if["false_last"] is not None:
                        add_edge(current_if["false_last"], merge_node.id)
                    # Falls sich der äußere if-Block im else-Zweig befindet,
                    # wird dessen letzter Knoten aktualisiert.
                    if pending_ifs and pending_ifs[-1]["in_false"]:
                        pending_ifs[-1]["false_last"] = merge_node.id
                    else:
                        last_node_id = merge_node.id
                else:
                    # Ohne else wird der letzte Knoten des wahren Zweigs übernommen.
                    last_node_id = current_if["true_last"] if current_if["true_last"] is not None else last_node_id
            continue

        # Verarbeitung von Aktivitätsknoten (Format: :Text;)
        m = re_activity.match(line)
        if m:
            label = m.group(1).strip()
            if pending_ifs:
                current_if = pending_ifs[-1]
                node = create_node(label, "rectangle", 0, 0, 120, 40)
                if not current_if["in_false"]:
                    if current_if["true_last"] is None:
                        add_edge(current_if["decision"], node.id, current_if["true_label"])
                    else:
                        add_edge(current_if["true_last"], node.id)
                    current_if["true_last"] = node.id
                else:
                    if current_if["false_last"] is None:
                        add_edge(current_if["decision"], node.id, current_if["false_label"])
                    else:
                        add_edge(current_if["false_last"], node.id)
                    current_if["false_last"] = node.id
                last_node_id = node.id
            else:
                node = create_node(label, "rectangle", 0, 0, 120, 40)
                if last_node_id is not None:
                    add_edge(last_node_id, node.id)
                last_node_id = node.id
            continue

        # Alle anderen Zeilen werden ignoriert

    # Falls der letzte Knoten nicht "Stop" ist, wird ein Stop-Knoten automatisch angehängt.
    if nodes and nodes[-1].label != "Stop":
        stop_node = create_node("Stop", "ellipse", 0, 0, 40, 40)
        if last_node_id is not None:
            add_edge(last_node_id, stop_node.id)

    return nodes, edges

def create_drawio_xml(nodes, edges):
    """
    Creates the XML content in draw.io format.
    """
    mxfile = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2025-02-10T00:00:00.000Z",
        "agent": "Python Script",
        "version": "15.7.7"
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": "diagramId", "name": "Page-1"})
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1264",
        "dy": "684",
        "grid": "1",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "1",
        "page": "1",
        "pageScale": "1",
        "pageWidth": "850",
        "pageHeight": "1100",
        "math": "0"
    })
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # Create nodes (mxCell for nodes)
    for node in nodes:
        if node.label in ["Start", "Stop"]:
            # Start and stop nodes: black filled with white text
            style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;fontColor=#ffffff;"
        elif node.shape == "ellipse":
            style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;"
        elif node.shape == "hexagon":
            # Decision nodes: hexagon with white text
            style = "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontSize=12;fontColor=#ffffff;fillColor=#00A5E1;strokeColor=none;size=10;"
        else:
            if node.label == "Merge":
                # Merge node as a rhombus in the same style as the condition
                style = "rhombus;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#00A5E1;fontColor=#ffffff;"
            else:
                style = "rounded=1;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#DCE9F1;"
        cell_attribs = {
            "id": node.id,
            "value": node.label,
            "style": style,
            "vertex": "1",
            "parent": "1"
        }
        cell = ET.SubElement(root, "mxCell", cell_attribs)
        geometry_attribs = {
            "x": str(node.x),
            "y": str(node.y),
            "width": str(node.width),
            "height": str(node.height),
            "as": "geometry"
        }
        ET.SubElement(cell, "mxGeometry", geometry_attribs)

    # Create edges (mxCell for edges)
    for edge in edges:
        cell_attribs = {
            "id": "e" + edge.id,
            "value": edge.label,
            "edge": "1",
            "source": edge.source,
            "target": edge.target,
            "parent": "1",
            "style": "edgeStyle=elbowEdgeStyle;elbow=vertical;strokeWidth=1.5;"
        }
        cell = ET.SubElement(root, "mxCell", cell_attribs)
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    # Create the XML string
    return ET.tostring(mxfile, encoding="utf-8", method="xml").decode("utf-8")

def create_json(nodes, edges):
    """
    Erzeugt eine JSON-Darstellung der Knoten und Kanten.

    Parameter:
      nodes - Liste der Knotenobjekte
      edges - Liste der Kantenobjekte

    Rückgabe:
      Ein String, der die JSON-Repräsentation enthält.
    """
    import json
    data = {
        "nodes": [
            {
                "id": node.id,
                "label": node.label,
                "shape": node.shape,
                "x": node.x,
                "y": node.y,
                "width": node.width,
                "height": node.height
            } for node in nodes
        ],
        "edges": [
            {
                "id": edge.id,
                "source": edge.source,
                "target": edge.target,
                "label": edge.label
            } for edge in edges
        ]
    }
    return json.dumps(data, indent=2, ensure_ascii=False)

def is_valid_plantuml_activitydiagram_string(plantuml_content):
    """
    Checks if the provided string contains a valid PlantUML activity diagram.

    Criteria:
      - The string must contain the markers @startuml and @enduml.
      - The string must include the keywords 'start' and 'stop'.
      - There must be at least one activity line (e.g., in the format :Text;)
        or alternatively an if-block with 'if' and 'endif'.

    Returns:
      - True if all criteria are met.
      - False otherwise.
    """
    # Check for the presence of @startuml and @enduml.
    if "@startuml" not in plantuml_content or "@enduml" not in plantuml_content:
        return False

    # Check for 'start' and 'stop' (case-insensitive).
    if "start" not in plantuml_content.lower() or "stop" not in plantuml_content.lower():
        return False

    import re
    # Check for at least one activity line in the format :Text;
    if not re.search(r":\s*(.+);", plantuml_content):
        # If no activity line is found, alternatively check for an if-block.
        if "if" not in plantuml_content.lower() or "endif" not in plantuml_content.lower():
            return False

    return True

def layout_activitydiagram(nodes, edges, vertical_spacing=80, horizontal_spacing=200, start_x=60, start_y=60):
    """
    Neues Layout für Aktivitätsdiagramme mittels rekursiver Tiefensuche (DFS) und Spaltenzuordnung,
    wobei für alle alternativen (else) Pfade eine neue Spalte verwendet wird und Merge-Knoten stets
    vertikal unterhalb der Knoten platziert werden, aus denen sie zusammenfließen. Zusätzlich 
    wird der Stop-Knoten immer ganz ans Ende (unterhalb aller anderen Knoten) gesetzt.

    Algorithmus:
      1. Initialisierung:
         - Ein Spaltenzähler (currentColumn) beginnt bei 1.
         - Es werden zwei Mappings erstellt, um jedem Knoten seine Spaltenzuordnung und einen
           vertikalen Index ("Order") zuzuweisen.
      
      2. Platzierung des Startknotens:
         - Der Startknoten (angenommen, das Label lautet "Start") wird der ersten Spalte 
           (currentColumn = 1) und Order 0 zugeordnet.
      
      3. Diagramm-Traversierung:
         - Das Diagramm wird mittels DFS traversiert.
         - Für Knoten, die keinem alternativen Pfad folgen (bspw. Ja-Pfade), verbleibt der Knoten
           in der aktuellen Spalte und der Order wird um 1 erhöht.
         - Für alle alternativen Pfade (else-Zweige bzw. alle Kanten, die explizit als "nein" oder
           als alternativer Ausgang eines Entscheidungsknotens identifiziert werden):
             → Es wird eine neue Spalte eröffnet (curr_col + 1) und der Order bleibt gleich,
                sodass der Knoten auf derselben vertikalen Höhe wie sein Ursprungknoten (bzw. die
                zugehörige Entscheidung) positioniert ist.
      
      4. Behandlung von Entscheidungsknoten:
         - Entscheidungsknoten (z. B. Hexagon) werden in der aktuellen Spalte platziert.
         - Bei ihren Ausgängen gilt: Der erste Ausgang folgt der Ja-Logik (Spalte bleibt, Order + 1),
           alle weiteren werden als alternative (else) Pfade betrachtet und erhalten eine neue Spalte.
      
      5. Merge-Knoten:
         - Merge-Knoten werden immer vertikal unterhalb der Knoten platziert, aus denen sie
           zusammenfließen. Daher wird der Order für einen Merge-Knoten als (aktueller Order + 1)
           gesetzt, unabhängig vom Pfad.
      
      6. Rekursive Anwendung und Abbruch:
         - Die DFS-Traversierung wird fortgesetzt, bis alle Knoten verarbeitet sind.
      
      7. Nachbearbeitung:
         - Der Stop-Knoten wird nach der Traversierung auf einen Order-Wert gesetzt, der größer ist als
           der aller anderen Knoten (sodass er ganz unten erscheint).
         - Abschließend werden die x- und y-Koordinaten der Knoten anhand der Spalten- und Order-Zuordnung
           berechnet:
               x = (start_x + x_offset) + (Spalte - 1) × horizontal_spacing - (node.width / 2)
               y = start_y + Order × vertical_spacing
         - Der Beginn der ersten Spalte erhält einen horizontalen Offset von 40 Pixeln.
    """
    # Mapping, um Knoten schnell anhand ihrer ID zu finden.
    node_by_id = {node.id: node for node in nodes}
    
    # Erstelle ein Adjazenzlisten-Mapping: Quelle -> Liste von (Ziel, Label)
    graph = {}
    for edge in edges:
        graph.setdefault(edge.source, []).append((edge.target, edge.label.lower()))
    
    # Dictionaries zur Speicherung der Spalten- und Order-Zuordnung für jeden Knoten.
    column_mapping = {}
    order_mapping = {}
    
    def dfs(node_id, curr_col, curr_order):
        # Aktualisiere (oder setze) die Spalten- und Order-Zuordnung.
        if node_id not in column_mapping:
            column_mapping[node_id] = curr_col
            order_mapping[node_id] = curr_order
        else:
            # Für Merge-Knoten wollen wir den maximalen Order (um sie unter den urspr. Knoten zu platzieren),
            # für alle anderen den minimalen Order.
            if node_by_id[node_id].label.lower() == "merge":
                order_mapping[node_id] = max(order_mapping[node_id], curr_order)
            else:
                order_mapping[node_id] = min(order_mapping[node_id], curr_order)
            column_mapping[node_id] = min(column_mapping[node_id], curr_col)
        
        # Gehe alle ausgehenden Kanten des aktuellen Knotens durch.
        children = graph.get(node_id, [])
        for index, (child_id, path_label) in enumerate(children):
            child_node = node_by_id.get(child_id)
            # Prüfe auf Merge-Knoten
            if child_node is not None and child_node.label.lower() == "merge":
                next_col = curr_col      # Merge-Knoten: gleiche Spalte
                next_order = curr_order + 1  # immer einen Schritt tiefer
            else:
                # Unterscheide ob wir aus einem Entscheidungsknoten (hexagon) kommen.
                if node_by_id[node_id].shape == "hexagon":
                    if index == 0:
                        # Erster Ausgang (Ja-Pfad)
                        next_col = curr_col
                        next_order = curr_order + 1
                    else:
                        # Alle alternativen Ausgänge (Else-Zweig): Neue Spalte, vertikale Höhe bleibt gleich.
                        next_col = curr_col + 1
                        next_order = curr_order
                else:
                    # Für Nicht-Entscheidungsknoten: Falls das Label explizit "nein" lautet, dann alternativer Pfad.
                    if path_label == "nein":
                        next_col = curr_col + 1
                        next_order = curr_order
                    else:
                        next_col = curr_col
                        next_order = curr_order + 1
            dfs(child_id, next_col, next_order)
    
    # Finde den Startknoten (angenommen, dessen Label lautet "Start")
    start_nodes = [node for node in nodes if node.label.lower() == "start"]
    if not start_nodes:
        start_nodes = [nodes[0]]
    
    # Starte die DFS-Traversierung von jedem Startknoten mit Spalte 1 und Order 0.
    for start_node in start_nodes:
        dfs(start_node.id, 1, 0)
    
    # Nachbearbeitung: Den Stop-Knoten immer ganz unten platzieren.
    if order_mapping:
        max_order = max(order_mapping.values())
    else:
        max_order = 0
    for node in nodes:
        if node.label.lower() == "stop":
            order_mapping[node.id] = max_order + 1
    
    # Gruppiere die Knoten basierend auf ihrer Spaltenzuordnung.
    columns = {}
    for node in nodes:
        col = column_mapping.get(node.id, 1)
        columns.setdefault(col, []).append(node)
    
    # Horizontaler Offset von 40 Pixeln für die erste Spalte.
    x_offset = 40

    # Weise jedem Knoten anhand der ermittelten Order einen y-Wert und anhand der Spalte einen x-Wert zu.
    for col, node_list in columns.items():
        # Sortiere die Knoten innerhalb der Spalte primär nach ihrem Order-Wert, sekundär nach ihrer ID.
        node_list.sort(key=lambda n: (order_mapping.get(n.id, 0), int(n.id)))
        for node in node_list:
            node.x = (start_x + x_offset) + (col - 1) * horizontal_spacing - node.width / 2
            node.y = start_y + order_mapping.get(node.id, 0) * vertical_spacing


def main():
    parser = argparse.ArgumentParser(
        description="Konvertiert ein PlantUML-Aktivitätsdiagramm in eine draw.io XML Datei oder in eine JSON Darstellung der Knoten und Kanten."
    )
    parser.add_argument("--input", required=True, help="Eingabe PlantUML Datei")
    parser.add_argument("--output", help="Ausgabe Datei (draw.io XML oder JSON)")
    parser.add_argument("--json", action="store_true", help="Gibt die Knoten und Kanten als JSON aus statt als XML.")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    if output_file is None:
        base, _ = os.path.splitext(input_file)
        if args.json:
            output_file = base + ".json"
        else:
            output_file = base + ".drawio"

    with open(input_file, "r", encoding="utf-8") as f:
        plantuml_content = f.read()

    if not is_valid_plantuml_activitydiagram_string(plantuml_content):
        print("Error: Die Datei ist kein gültiges PlantUML Aktivitätsdiagramm.")
        sys.exit(1)

    nodes, edges = parse_plantuml_activity(plantuml_content)
    layout_activitydiagram(nodes, edges)

    if args.json:
        json_output = create_json(nodes, edges)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_output)
        print("JSON Datei erstellt:", output_file)
    else:
        xml_content = create_drawio_xml(nodes, edges)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print("Draw.io Datei erstellt:", output_file)

if __name__ == "__main__":
    main()