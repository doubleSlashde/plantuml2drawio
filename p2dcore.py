#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
import argparse
import os
import re  # Import am Anfang der Datei statt in der Funktion

# Vordefinierte Regex-Muster für bessere Performance
RE_ACTIVITY = re.compile(r":\s*(.+?);", re.DOTALL)  # DOTALL erlaubt Newlines in Aktivitäten
RE_IF_BLOCK = re.compile(r"if\s*\(.+?\).+?endif", re.DOTALL | re.IGNORECASE)

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
      - Aktivitätstexte können mehrzeilig sein (zwischen : und ;).
    """
    import re

    # Prekompilierte Regex-Pattern für bessere Performance
    re_if = re.compile(r"if\s*\((.+)\)\s*then\s*\((.+)\)", re.IGNORECASE)
    re_else = re.compile(r"else\s*\((.+)\)", re.IGNORECASE)
    re_activity_start = re.compile(r":(.*)")
    re_activity_end = re.compile(r"(.*);")
    re_skip_line = re.compile(r"^\s*(?:$|'|//|@startuml|@enduml)", re.IGNORECASE)

    # Initialisierung der Datenstrukturen
    nodes = []
    edges = []
    last_node_id = None
    node_counter = 2  # Die IDs "0" und "1" sind durch draw.io vorbelegt
    edge_counter = 1
    pending_ifs = []  # Stack für verschachtelte if-Blöcke
    
    # Hilfsvariablen für mehrzeilige Aktivitäten
    in_activity = False
    activity_text = []

    # Hilfsfunktionen
    def create_node(label, shape, width=120, height=40):
        """Erstellt einen neuen Knoten mit optimierten Standardwerten"""
        nonlocal node_counter
        node_id = str(node_counter)
        node = Node(id=node_id, label=label, shape=shape,
                   x=0, y=0, width=width, height=height)
        nodes.append(node)
        node_counter += 1
        return node

    def add_edge(source, target, label=""):
        """Erstellt eine neue Kante zwischen zwei Knoten"""
        nonlocal edge_counter
        edge_id = str(edge_counter)
        edge = Edge(id=edge_id, source=source, target=target, label=label)
        edges.append(edge)
        edge_counter += 1
        return edge
        
    def process_activity(text):
        """Verarbeitet einen Aktivitätstext und erstellt den entsprechenden Knoten"""
        nonlocal last_node_id
        label = text.strip()
        
        # Neue Aktivität erstellen
        node = create_node(label, "rectangle")
        
        # Verbindung zum vorherigen Knoten erstellen
        if pending_ifs:
            # Aktivität innerhalb eines if-Blocks
            current_if = pending_ifs[-1]
            
            if not current_if["in_false"]:
                # True-Zweig
                if current_if["true_last"] is None:
                    add_edge(current_if["decision"], node.id, current_if["true_label"])
                else:
                    add_edge(current_if["true_last"], node.id)
                current_if["true_last"] = node.id
            else:
                # False-Zweig
                if current_if["false_last"] is None:
                    add_edge(current_if["decision"], node.id, current_if["false_label"])
                else:
                    add_edge(current_if["false_last"], node.id)
                current_if["false_last"] = node.id
        elif last_node_id is not None:
            # Normale Aktivität außerhalb eines if-Blocks
            add_edge(last_node_id, node.id)
            
        last_node_id = node.id
        return node

    # Verarbeitung der einzelnen Zeilen
    lines = plantuml_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1  # Nächste Zeile vorbereiten
        
        # Überspringe Kommentare, leere Zeilen und Diagramm-Markierungen
        if re_skip_line.match(line):
            continue

        line_lower = line.lower()
        
        # Wenn wir uns in einer mehrzeiligen Aktivität befinden
        if in_activity:
            m_end = re_activity_end.match(line)
            if m_end:
                # Ende der Aktivität gefunden
                activity_text.append(m_end.group(1))
                process_activity("\n".join(activity_text))
                in_activity = False
                activity_text = []
            else:
                # Sammle weiteren Text
                activity_text.append(line)
            continue

        # Start- und Stop-Knoten verarbeiten (häufige Fälle zuerst prüfen)
        if line_lower == "start":
            node = create_node("Start", "ellipse", 40, 40)
            if last_node_id is not None:
                add_edge(last_node_id, node.id)
            last_node_id = node.id
            continue

        if line_lower == "stop":
            node = create_node("Stop", "ellipse", 40, 40)
            if last_node_id is not None:
                add_edge(last_node_id, node.id)
            last_node_id = node.id
            continue

        # Aktivitäts-Knoten verarbeiten (häufiger Fall)
        m_start = re_activity_start.match(line)
        if m_start:
            text = m_start.group(1)
            if ";" in text:  # Einzeilige Aktivität
                process_activity(text.split(";")[0])
            else:  # Beginn einer mehrzeiligen Aktivität
                in_activity = True
                activity_text = [text]
            continue

        # Bedingungen und Kontrollstrukturen verarbeiten
        # if-Bedingung
        m_if = re_if.match(line)
        if m_if:
            condition, true_label = m_if.group(1).strip(), m_if.group(2).strip()
            node = create_node(condition, "hexagon", 80, 40)
            if last_node_id is not None:
                add_edge(last_node_id, node.id)
            last_node_id = node.id
            
            # If-Block auf den Stack legen
            pending_ifs.append({
                "decision": node.id,
                "true_label": true_label,
                "true_last": None,   # Letzter Knoten des wahren Zweigs
                "false_label": None, # Beschriftung für else-Zweig
                "false_last": None,  # Letzter Knoten des falschen Zweigs
                "in_false": False    # Aktueller Zweig (true/false)
            })
            continue

        # else-Zweig
        m_else = re_else.match(line)
        if m_else and pending_ifs:
            pending_ifs[-1]["false_label"] = m_else.group(1).strip()
            pending_ifs[-1]["in_false"] = True
            continue

        # endif-Schluss
        if line_lower.startswith("endif"):
            if pending_ifs:
                current_if = pending_ifs.pop()
                if current_if["false_label"] is not None:
                    # Mit else-Zweig: Merge-Knoten erstellen
                    merge_node = create_node("Merge", "rhombus", 50, 50)
                    
                    # Verbindungen zum Merge-Knoten erstellen
                    if current_if["true_last"] is not None:
                        add_edge(current_if["true_last"], merge_node.id)
                    if current_if["false_last"] is not None:
                        add_edge(current_if["false_last"], merge_node.id)
                    
                    # Letzten Knoten aktualisieren
                    if pending_ifs and pending_ifs[-1]["in_false"]:
                        pending_ifs[-1]["false_last"] = merge_node.id
                    else:
                        last_node_id = merge_node.id
                else:
                    # Ohne else: Letzten Knoten des wahren Zweigs übernehmen
                    last_node_id = current_if["true_last"] if current_if["true_last"] is not None else last_node_id
            continue

    # Abschluss: Falls kein Stop-Knoten am Ende steht, einen automatisch anhängen
    if nodes and nodes[-1].label != "Stop":
        stop_node = create_node("Stop", "ellipse", 40, 40)
        if last_node_id is not None:
            add_edge(last_node_id, stop_node.id)

    return nodes, edges

def create_drawio_xml(nodes, edges):
    """
    Erstellt den XML-Inhalt im draw.io-Format.
    
    Parameter:
      nodes - Liste der Knotenobjekte
      edges - Liste der Kantenobjekte
    
    Rückgabe:
      XML-String im draw.io-Format
    """
    # Konstanten für Knoten-Stile
    STYLES = {
        "start_stop": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;fontColor=#ffffff;",
        "ellipse": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;",
        "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontSize=12;fontColor=#ffffff;fillColor=#00A5E1;strokeColor=none;size=10;",
        "merge": "rhombus;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#00A5E1;fontColor=#ffffff;",
        "activity": "rounded=1;whiteSpace=wrap;html=1;strokeColor=none;fillColor=#DCE9F1;",
        "edge": "edgeStyle=elbowEdgeStyle;elbow=vertical;strokeWidth=1.5;"
    }
    
    # Grundgerüst des XML erstellen
    def create_base_xml():
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
        return mxfile, root
    
    # Stil für einen Knoten basierend auf seinem Typ auswählen
    def get_node_style(node):
        if node.label in ["Start", "Stop"]:
            return STYLES["start_stop"]
        elif node.shape == "ellipse":
            return STYLES["ellipse"]
        elif node.shape == "hexagon":
            return STYLES["hexagon"] 
        elif node.label == "Merge":
            return STYLES["merge"]
        else:
            return STYLES["activity"]
    
    # Knoten zum XML hinzufügen
    def add_nodes_to_xml(root, nodes):
        for node in nodes:
            style = get_node_style(node)
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
    
    # Kanten zum XML hinzufügen
    def add_edges_to_xml(root, edges):
        for edge in edges:
            cell_attribs = {
                "id": "e" + edge.id,
                "value": edge.label,
                "edge": "1",
                "source": edge.source,
                "target": edge.target,
                "parent": "1",
                "style": STYLES["edge"]
            }
            cell = ET.SubElement(root, "mxCell", cell_attribs)
            ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    
    # Hauptlogik
    mxfile, root = create_base_xml()
    add_nodes_to_xml(root, nodes)
    add_edges_to_xml(root, edges)
    
    # XML als String zurückgeben
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

def is_valid_plantuml_activitydiagram(plantuml_content):
    """
    Prüft, ob der übergebene String ein gültiges PlantUML-Aktivitätsdiagramm enthält.

    Kriterien:
      - Der String muss die Markierungen @startuml und @enduml enthalten.
      - Der String muss die Schlüsselwörter 'start' und 'stop' enthalten (Groß-/Kleinschreibung wird ignoriert).
      - Es muss mindestens eine Aktivitätszeile (im Format :Text;) oder alternativ
        ein if-Block mit 'if' und 'endif' vorhanden sein.

    Rückgabe:
      - True, wenn alle Kriterien erfüllt sind.
      - False, andernfalls.
    """
    # Schnelle String-Überprüfungen zuerst für bessere Performance
    if "@startuml" not in plantuml_content or "@enduml" not in plantuml_content:
        return False

    plantuml_lower = plantuml_content.lower()
    if "start" not in plantuml_lower or "stop" not in plantuml_lower:
        return False

    # Überprüfung auf Aktivitätszeile oder if-Block mit kompilierten Regex-Mustern
    if not RE_ACTIVITY.search(plantuml_content):
        # Wenn keine Aktivitätszeile gefunden wurde, alternativ nach einem if-Block suchen
        if not RE_IF_BLOCK.search(plantuml_content):
            return False

    return True

def layout_activitydiagram(nodes, edges, vertical_spacing=100, horizontal_spacing=200, start_x=60, start_y=60):
    """
    Neues Layout für Aktivitätsdiagramme mittels rekursiver Tiefensuche (DFS) und Spaltenzuordnung,
    wobei für alle alternativen (else) Pfade eine neue Spalte verwendet wird und Merge-Knoten stets
    vertikal unterhalb der Knoten platziert werden, aus denen sie zusammenfließen. Zusätzlich 
    wird der Stop-Knoten immer ganz ans Ende (unterhalb aller anderen Knoten) gesetzt.

    Parameter:
      nodes - Liste der Knotenobjekte
      edges - Liste der Kantenobjekte
      vertical_spacing - Vertikaler Abstand zwischen Knoten
      horizontal_spacing - Horizontaler Abstand zwischen Spalten
      start_x - Startkoordinate X
      start_y - Startkoordinate Y
    """
    from collections import defaultdict
    import sys
    
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
    def calculate_next_position(parent_id, child_id, path_label, index, curr_col, curr_order):
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
                node.x = (start_x + x_offset) + (col - 1) * horizontal_spacing - node.width / 2
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

def process_file(input_file, output_file, output_json=False):
    """
    Verarbeitet eine PlantUML-Datei und erstellt die entsprechende Ausgabedatei.
    
    Args:
        input_file: Pfad zur Eingabedatei
        output_file: Pfad zur Ausgabedatei
        output_json: Bei True wird JSON ausgegeben, sonst XML
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            plantuml_content = f.read()

        if not is_valid_plantuml_activitydiagram(plantuml_content):
            print(f"Error: The file '{input_file}' does not contain a valid PlantUML activity diagram.")
            return False

        nodes, edges = parse_plantuml_activity(plantuml_content)
        layout_activitydiagram(nodes, edges)

        output_format = "JSON" if output_json else "Draw.io XML"
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if output_json:
                    json_output = create_json(nodes, edges)
                    f.write(json_output)
                else:
                    xml_content = create_drawio_xml(nodes, edges)
                    f.write(xml_content)
            print(f"{output_format} file successfully created: {output_file}")
            return True
        except IOError as e:
            print(f"Error writing output file '{output_file}': {e}")
            return False
            
    except IOError as e:
        print(f"Error reading input file '{input_file}': {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during processing: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Converts a PlantUML activity diagram to a draw.io XML file or a JSON representation of nodes and edges."
    )
    parser.add_argument("--input", required=True, help="Input PlantUML file")
    parser.add_argument("--output", help="Output file (draw.io XML or JSON)")
    parser.add_argument("--json", action="store_true", help="Output nodes and edges as JSON instead of XML.")
    args = parser.parse_args()

    # Bestimme den Ausgabedateinamen, falls nicht angegeben
    input_file = args.input
    output_file = args.output
    if output_file is None:
        base, _ = os.path.splitext(input_file)
        extension = ".json" if args.json else ".drawio"
        output_file = base + extension

    # Verarbeite die Datei
    success = process_file(input_file, output_file, args.json)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()