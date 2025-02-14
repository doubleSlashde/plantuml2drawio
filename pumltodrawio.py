#!/usr/bin/env python3
import sys
import re
import xml.etree.ElementTree as ET

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

def parse_plantuml(filename):
    """
    Parst eine vereinfachte Variante eines PlantUML Aktivitätsdiagramms.
    Unterstützte Elemente:
      - start und stop
      - Aktivitäten in der Form :Text;
      - if (Bedingung) then (ja)
      - else (alternativer Text)
      - endif
    Die Knoten werden dabei vertikal positioniert.

    Wichtig:
      - Wird ein if gefunden, erzeugen wir einen Entscheidungsknoten,
        dessen Ausgang "Ja" beschriftet wird (den wir aus der then-Klammer übernehmen).
      - Bei der else-Anweisung wird der Inhalt der Klammer als Label für den
        alternativen Ausgang genutzt. Der erste Knoten des False-Zweigs wird
        über diesen Ausgang verbunden.
      - Am Ende eines if-Blocks (endif) wird – falls ein else-Zweig existiert –
        ein Merge-Knoten erstellt, der beide Zweige zusammenführt.
      - Falls eine Aktion (oder ein Zweig) am Ende steht und kein weiterer
        Knoten (weder Aktion noch Bedingung) folgt, wird automatisch ein Pfeil zum
        Stop-Knoten erstellt.
      - Neu: Die ersten Aktionen im True- und False-Zweig werden auf einer gemeinsamen Höhe
        (baseline) positioniert.
    """
    import re
    import xml.etree.ElementTree as ET

    # Datei einlesen
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    nodes = []
    edges = []
    last_node_id = None
    node_counter = 2  # Die IDs "0" und "1" werden in draw.io vorgegeben.
    edge_counter = 1

    # Anfangskoordinaten und Layout-Parameter
    current_x = 60
    current_y = 60
    vertical_spacing = 80

    # Statt einer einzelnen pending_if verwenden wir einen Stack für verschachtelte if-Blöcke.
    # Zusätzlich speichern wir für jeden If-Block die Ausgangskoordinate ("baseline_y")
    # und separate y-Koordinaten für den True- und False-Zweig.
    pending_ifs = []

    for line in lines:
        line = line.strip()
        # Kommentare und leere Zeilen überspringen
        if not line or line.startswith("'") or line.startswith("//"):
            continue
        if line.startswith("@startuml") or line.startswith("@enduml"):
            continue

        # Start-Knoten
        if line.lower() == "start":
            node = Node(id=str(node_counter), label="Start", shape="ellipse",
                        x=current_x, y=current_y, width=40, height=40)
            nodes.append(node)
            if last_node_id is not None:
                edges.append(Edge(id=str(edge_counter), source=last_node_id, target=node.id))
                edge_counter += 1
            last_node_id = node.id
            node_counter += 1
            current_y += vertical_spacing
            continue

        # Stop-Knoten
        if line.lower() == "stop":
            node = Node(id=str(node_counter), label="Stop", shape="ellipse",
                        x=current_x, y=current_y, width=40, height=40)
            nodes.append(node)
            if last_node_id is not None:
                edges.append(Edge(id=str(edge_counter), source=last_node_id, target=node.id))
                edge_counter += 1
            last_node_id = node.id
            node_counter += 1
            current_y += vertical_spacing
            continue

        # if-Bedingung: if (Bedingung) then (Ja)
        m = re.match(r"if\s*\((.+)\)\s*then\s*\((.+)\)", line, re.IGNORECASE)
        if m:
            condition = m.group(1).strip()
            true_label = m.group(2).strip()  # Beschriftung des "Ja"-Ausgangs

            # Wenn wir in einem verschachtelten Block sind, verwenden wir den lokalen y-Wert
            if pending_ifs:
                parent = pending_ifs[-1]
                if parent["in_false"]:
                    node_y = parent["false_y"]
                    x_coord = current_x + 150
                    parent["false_y"] += vertical_spacing
                else:
                    node_y = parent["true_y"]
                    x_coord = current_x
                    parent["true_y"] += vertical_spacing
            else:
                node_y = current_y
                x_coord = current_x
                current_y += vertical_spacing

            # Erzeuge den Entscheidungsknoten (hexagon)
            node = Node(id=str(node_counter), label=condition, shape="hexagon",
                        x=x_coord, y=node_y, width=100, height=40)
            nodes.append(node)
            if last_node_id is not None:
                edges.append(Edge(id=str(edge_counter), source=last_node_id, target=node.id))
                edge_counter += 1
            last_node_id = node.id
            node_counter += 1

            # Für den If-Block: setze die Baseline für beide Zweige.
            # Bei verschachtelten Ifs orientiert sich die Baseline am Knoten des if-Befehls.
            if pending_ifs:
                baseline_y = node_y + vertical_spacing
            else:
                baseline_y = current_y
            pending_ifs.append({
                "decision": node.id,
                "true_label": true_label,
                "true_last": None,   # Wird gesetzt, wenn der True-Zweig beginnt
                "false_label": None,  # Später gesetzt, wenn ein else auftaucht
                "false_last": None,   # Wird gesetzt, wenn der False-Zweig beginnt
                "in_false": False,    # Kennzeichnet, in welchem Zweig wir uns befinden
                "baseline_y": baseline_y,  # Gemeinsame Ausgangskoordinate für beide Zweige
                "true_y": baseline_y,      # Lokaler y-Zähler für den True-Zweig
                "false_y": baseline_y      # Lokaler y-Zähler für den False-Zweig
            })
            continue

        # else-Zweig: else (Alternativtext)
        m = re.match(r"else\s*\((.+)\)", line, re.IGNORECASE)
        if m and pending_ifs:
            pending_ifs[-1]["false_label"] = m.group(1).strip()
            pending_ifs[-1]["in_false"] = True
            continue

        # endif: schließt den aktuellsten if-Block ab
        if line.lower().startswith("endif"):
            if pending_ifs:
                current_if = pending_ifs.pop()
                if current_if["false_label"] is not None:
                    # Bei einem else-Zweig: merge_node an der maximalen y-Koordinate beider Zweige
                    merge_y = max(current_if["true_y"], current_if["false_y"])
                    merge_node = Node(id=str(node_counter), label="Merge", shape="rhombus",
                                      x=current_x, y=merge_y, width=50, height=50)
                    nodes.append(merge_node)
                    if current_if["true_last"] is not None:
                        edges.append(Edge(id=str(edge_counter), source=current_if["true_last"], target=merge_node.id))
                        edge_counter += 1
                    if current_if["false_last"] is not None:
                        edges.append(Edge(id=str(edge_counter), source=current_if["false_last"], target=merge_node.id))
                        edge_counter += 1

                    # Falls ein verschachtelter If im False-Zweig existiert,
                    # aktualisieren wir den Eltern-If-Block, sodass dessen false_last
                    # nun auf den inneren Merge-Knoten zeigt.
                    if pending_ifs and pending_ifs[-1]["in_false"]:
                        pending_ifs[-1]["false_last"] = merge_node.id
                    else:
                        last_node_id = merge_node.id

                    node_counter += 1
                    current_y = merge_y + vertical_spacing
                else:
                    # Kein else-Zweig vorhanden: aktueller y-Wert entspricht dem True-Zweig
                    current_y = current_if["true_y"]
            continue

        # Aktivitätsknoten (z. B. :Schritt;)
        m = re.match(r":(.+);", line)
        if m:
            label = m.group(1).strip()
            if pending_ifs:
                current_if = pending_ifs[-1]
                if not current_if["in_false"]:
                    # True-Zweig: benutze den aktuellen lokalen y-Wert des True-Zweigs
                    node_y = current_if["true_y"]
                    x_coord = current_x
                    node = Node(id=str(node_counter), label=label, shape="rectangle",
                                x=x_coord, y=node_y, width=100, height=40)
                    nodes.append(node)
                    if current_if["true_last"] is None:
                        # Verbinde vom Entscheidungsknoten mit Label "Ja"
                        edges.append(Edge(id=str(edge_counter), source=current_if["decision"], target=node.id, label=current_if["true_label"]))
                        edge_counter += 1
                    else:
                        edges.append(Edge(id=str(edge_counter), source=current_if["true_last"], target=node.id))
                        edge_counter += 1
                    current_if["true_last"] = node.id
                    # Erhöhe den lokalen y-Zähler des True-Zweigs
                    current_if["true_y"] = node_y + vertical_spacing
                    last_node_id = node.id
                else:
                    # False-Zweig: benutze den lokalen y-Wert des False-Zweigs
                    node_y = current_if["false_y"]
                    x_coord = current_x + 150
                    node = Node(id=str(node_counter), label=label, shape="rectangle",
                                x=x_coord, y=node_y, width=100, height=40)
                    nodes.append(node)
                    if current_if["false_last"] is None:
                        edges.append(Edge(id=str(edge_counter), source=current_if["decision"], target=node.id, label=current_if["false_label"]))
                        edge_counter += 1
                    else:
                        edges.append(Edge(id=str(edge_counter), source=current_if["false_last"], target=node.id))
                        edge_counter += 1
                    current_if["false_last"] = node.id
                    current_if["false_y"] = node_y + vertical_spacing
                    last_node_id = node.id
                node_counter += 1
            else:
                # Normale Aktivitätsknoten (außerhalb eines if-Blocks)
                node = Node(id=str(node_counter), label=label, shape="rectangle",
                            x=current_x, y=current_y, width=100, height=40)
                nodes.append(node)
                if last_node_id is not None:
                    edges.append(Edge(id=str(edge_counter), source=last_node_id, target=node.id))
                    edge_counter += 1
                last_node_id = node.id
                node_counter += 1
                current_y += vertical_spacing
            continue

        # Weitere Zeilen werden ignoriert oder können hier ergänzt werden.

    # Falls der letzte Knoten (bei einer Aktion, der auf keinen weiteren Knoten zeigt)
    # nicht bereits ein Stop-Knoten ist, wird automatisch ein Stop-Knoten hinzugefügt.
    if nodes and nodes[-1].label != "Stop":
        stop_node = Node(
            id=str(node_counter),
            label="Stop",
            shape="ellipse",
            x=current_x,
            y=current_y,
            width=40,
            height=40
        )
        nodes.append(stop_node)
        if last_node_id is not None:
            edges.append(Edge(id=str(edge_counter), source=last_node_id, target=stop_node.id))
            edge_counter += 1
        node_counter += 1
        current_y += vertical_spacing

    return nodes, edges

def create_drawio_xml(nodes, edges):
    """
    Erzeugt den XML-Inhalt im draw.io-Format.
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

    # Erzeuge Knoten (mxCell für Knoten)
    for node in nodes:
        if node.label in ["Start", "Stop"]:
            # Start- und Endknoten: schwarz gefüllt, weißer Text
            style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;fontColor=#ffffff;"
        elif node.shape == "ellipse":
            style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;"
        elif node.shape == "hexagon":
            # Entscheidungsknoten: Rhombus mit weißer Schrift
            style = "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontSize=12;fontColor=#ffffff;fillColor=#00A5E1;strokeColor=none;size=10;"
        else:
            if node.label == "Merge":
                # Merge-Knoten als Rhombus im gleichen Stil wie die Bedingung
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

    # Erzeuge Kanten (mxCell für Kanten)
    for edge in edges:
        cell_attribs = {
            "id": "e" + edge.id,
            "value": edge.label,
            "edge": "1",
            "source": edge.source,
            "target": edge.target,
            "parent": "1",
            "style": "edgeStyle=elbowEdgeStyle;elbow=vertical;"
        }
        cell = ET.SubElement(root, "mxCell", cell_attribs)
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    # Erzeuge den XML-String
    return ET.tostring(mxfile, encoding="utf-8", method="xml").decode("utf-8")

def main():
    if len(sys.argv) != 3:
        print("Usage: {} <input_plantuml_file> <output_drawio_file>".format(sys.argv[0]))
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    nodes, edges = parse_plantuml(input_file)
    xml_content = create_drawio_xml(nodes, edges)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print("Draw.io Datei wurde erstellt:", output_file)

if __name__ == "__main__":
    main()