#!/usr/bin/env python3
import sys
import argparse
import os
import re
from typing import Tuple, Dict, Optional, List, Any, Union
from modules.activity_processor import (
    is_valid_activity_diagram,
    parse_activity_diagram,
    layout_activity_diagram,
    create_activity_drawio_xml,
    create_json,
    Node,
    Edge
)

# Konstanten
OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_XML = "Draw.io XML"
DEFAULT_JSON_EXT = ".json"
DEFAULT_DRAWIO_EXT = ".drawio"
DIAGRAM_TYPE_ACTIVITY = "activity"
DIAGRAM_TYPE_NOT_PLANTUML = "not_plantuml"

# Vordefinierte Regex-Muster für bessere Performance
RE_ACTIVITY = re.compile(r":\s*(.+?);", re.DOTALL)  # DOTALL erlaubt Newlines in Aktivitäten
RE_IF_BLOCK = re.compile(r"if\s*\(.+?\).+?endif", re.DOTALL | re.IGNORECASE)
RE_SEQUENCE_ARROW = re.compile(r"[^\s]+\s*[-=]+>|<[-=]+\s*[^\s]+")
RE_CLASS_RELATION = re.compile(r"[^\s]+\s*[<\-o\*\+\^\.#\}]+\-\-+[<\-o\*\+\^\.#\}]*\s*[^\s]+")
RE_CLASS_DEF = re.compile(r"class\s+[\w\"]+|interface\s+[\w\"]+|enum\s+[\w\"]+")
RE_USECASE = re.compile(r"\([^\)]+\)|usecase\s+[\w\"]+")
RE_ACTOR = re.compile(r":[^\:]+:|actor\s+[\w\"]+")
RE_COMPONENT = re.compile(r"component\s+[\w\"]+|\[[^\]]+\]")
RE_STATE = re.compile(r"state\s+[\w\"]+")
RE_OBJECT = re.compile(r"object\s+[\w\"]+")
RE_ENTITY = re.compile(r"entity\s+[\w\"]+")
RE_NODE = re.compile(r"node\s+[\w\"]+")
RE_PACKAGE = re.compile(r"package\s+[\w\"]+")

def determine_plantuml_diagram_type(plantuml_content: str) -> str:
    """
    Determines the type of PlantUML diagram based on its content.
    
    Supported diagram types:
    - Activity diagram
    - Sequence diagram
    - Class diagram
    - Use case diagram
    - Component diagram
    - State diagram
    - Object diagram
    - Entity-relationship diagram (ERD)
    - Deployment diagram
    - And others (fallback)
    
    Args:
        plantuml_content: String containing the PlantUML diagram code
        
    Returns:
        String indicating the diagram type
    """
    # First, check if content is a valid PlantUML file
    if "@startuml" not in plantuml_content or "@enduml" not in plantuml_content:
        return DIAGRAM_TYPE_NOT_PLANTUML
    
    # Convert to lowercase for easier keyword detection
    content_lower = plantuml_content.lower()
    
    # Activity diagram detection
    activity_indicators = 0
    if "start" in content_lower and "stop" in content_lower:
        activity_indicators += 2
    if RE_ACTIVITY.search(plantuml_content):
        activity_indicators += 1
    if RE_IF_BLOCK.search(plantuml_content):
        activity_indicators += 1
    
    # Sequence diagram detection
    sequence_indicators = 0
    if RE_SEQUENCE_ARROW.search(plantuml_content):
        sequence_indicators += 1  # Reduced weight as this can appear in other diagrams too
    if "participant" in content_lower or "actor" in content_lower and "->" in plantuml_content:
        sequence_indicators += 1
    if "activate" in content_lower or "deactivate" in content_lower:
        sequence_indicators += 2  # Increased weight as these are specific to sequence diagrams
    
    # Class diagram detection
    class_indicators = 0
    if RE_CLASS_DEF.search(plantuml_content):
        class_indicators += 2
    if RE_CLASS_RELATION.search(plantuml_content):
        class_indicators += 1
    if "abstract" in content_lower or "static" in content_lower or "private" in content_lower:
        class_indicators += 1
    if "extends" in content_lower or "implements" in content_lower:
        class_indicators += 1
    
    # Use case diagram detection
    usecase_indicators = 0
    if RE_USECASE.search(plantuml_content):
        usecase_indicators += 2
    if RE_ACTOR.search(plantuml_content):
        usecase_indicators += 2
    
    # Component diagram detection
    component_indicators = 0
    if RE_COMPONENT.search(plantuml_content):
        component_indicators += 2  # Adjusted weight 
    if "interface" in content_lower and "[" in plantuml_content and "]" in plantuml_content:
        component_indicators += 1
    if RE_PACKAGE.search(plantuml_content) and not RE_STATE.search(plantuml_content):
        component_indicators += 1  # Packages are common in component diagrams
    if "database" in content_lower or "queue" in content_lower:
        component_indicators += 1  # These are often used in component diagrams
    
    # State diagram detection
    state_indicators = 0
    if RE_STATE.search(plantuml_content):
        state_indicators += 3  # Increased weight for state keyword
    if "[*]" in plantuml_content:  # Start/end state notation is very specific to state diagrams
        state_indicators += 2
    if "state" in content_lower and "{" in plantuml_content and "}" in plantuml_content:
        state_indicators += 1  # Nested states are common in state diagrams
    
    # Object diagram detection
    object_indicators = 0
    if RE_OBJECT.search(plantuml_content):
        object_indicators += 2
    
    # Entity-relationship diagram detection (ERD)
    erd_indicators = 0
    if RE_ENTITY.search(plantuml_content):
        erd_indicators += 2
    if "entity" in content_lower and ("||--o{" in plantuml_content or "*--" in plantuml_content):
        erd_indicators += 1
    
    # Deployment diagram detection
    deployment_indicators = 0
    if RE_NODE.search(plantuml_content):
        deployment_indicators += 2
    
    # Determine the diagram type based on the highest indicator count
    indicators = {
        DIAGRAM_TYPE_ACTIVITY: activity_indicators,
        "sequence": sequence_indicators,
        "class": class_indicators,
        "usecase": usecase_indicators,
        "component": component_indicators,
        "state": state_indicators,
        "object": object_indicators,
        "erd": erd_indicators,
        "deployment": deployment_indicators
    }
    
    # Find the diagram type with the highest indicator count
    max_indicators = 0
    diagram_type = "unknown"
    
    for dtype, count in indicators.items():
        if count > max_indicators:
            max_indicators = count
            diagram_type = dtype
    
    return diagram_type

def process_diagram(plantuml_content: str, output_json: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """
    Verarbeitet einen PlantUML-Inhalt und erzeugt die entsprechende XML- oder JSON-Darstellung.
    
    Args:
        plantuml_content: Inhalt des PlantUML-Diagramms
        output_json: Bei True wird JSON ausgegeben, sonst XML
    
    Returns:
        Bei Erfolg: Tuple aus (String mit XML oder JSON, Ausgabeformat-Beschreibung)
        Bei Fehler: (None, None)
    """
    try:
        nodes, edges = parse_activity_diagram(plantuml_content)
        layout_activity_diagram(nodes, edges)

        output_format = OUTPUT_FORMAT_JSON if output_json else OUTPUT_FORMAT_XML
        
        if output_json:
            output_content = create_json(nodes, edges)
        else:
            output_content = create_activity_drawio_xml(nodes, edges)
            
        return output_content, output_format
            
    except Exception as e:
        print(f"Unexpected error during processing: {e}")
        return None, None

def read_plantuml_file(file_path: str) -> Optional[str]:
    """
    Liest eine PlantUML-Datei ein und gibt den Inhalt zurück.
    
    Args:
        file_path: Pfad zur einzulesenden Datei
        
    Returns:
        Inhalt der Datei als String oder None bei Fehler
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError as e:
        print(f"Error reading input file '{file_path}': {e}")
        return None

def write_output_file(content: str, file_path: str) -> bool:
    """
    Schreibt den gegebenen Inhalt in eine Datei.
    
    Args:
        content: Zu schreibender Inhalt
        file_path: Pfad zur Ausgabedatei
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"Error writing output file '{file_path}': {e}")
        return False

def get_output_file_path(input_file: str, output_file: Optional[str], is_json: bool) -> str:
    """
    Bestimmt den Pfad zur Ausgabedatei basierend auf Eingabedatei und Ausgabeformat.
    
    Args:
        input_file: Pfad zur Eingabedatei
        output_file: Optionaler Pfad zur Ausgabedatei
        is_json: True wenn JSON-Format, False wenn Draw.io-XML-Format
        
    Returns:
        Pfad zur Ausgabedatei
    """
    if output_file:
        return output_file
        
    base, _ = os.path.splitext(input_file)
    extension = DEFAULT_JSON_EXT if is_json else DEFAULT_DRAWIO_EXT
    return base + extension

def handle_info_request(diagram_type: str) -> None:
    """
    Zeigt Informationen über den erkannten Diagrammtyp an.
    
    Args:
        diagram_type: Erkannter Diagrammtyp
    """
    print(f"Diagram type: {diagram_type}")
    if diagram_type == DIAGRAM_TYPE_NOT_PLANTUML:
        print("This does not appear to be a valid PlantUML file.")
    elif diagram_type != DIAGRAM_TYPE_ACTIVITY:
        print("Note: Currently only activity diagrams are supported for conversion.")

def main() -> None:
    """
    Hauptfunktion des Programms.
    Parst Kommandozeilenargumente, liest PlantUML-Datei ein, 
    bestimmt den Diagrammtyp, verarbeitet das Diagramm und 
    schreibt die Ausgabe in eine Datei.
    """
    # Kommandozeilenargumente parsen
    parser = argparse.ArgumentParser(
        description="Converts a PlantUML activity diagram to a draw.io XML file or a JSON representation of nodes and edges."
    )
    parser.add_argument("--input", required=True, help="Input PlantUML file")
    parser.add_argument("--output", help="Output file (draw.io XML or JSON)")
    parser.add_argument("--json", action="store_true", help="Output nodes and edges as JSON instead of XML.")
    parser.add_argument("--info", action="store_true", help="Only display information about the diagram type without converting.")
    args = parser.parse_args()

    # Eingabedatei einlesen
    plantuml_content = read_plantuml_file(args.input)
    if plantuml_content is None:
        sys.exit(1)
        
    # Diagrammtyp bestimmen
    diagram_type = determine_plantuml_diagram_type(plantuml_content)
    
    # Nur Informationen anzeigen, falls angefordert
    if args.info:
        handle_info_request(diagram_type)
        sys.exit(0)
    
    # Ausgabedatei bestimmen
    output_file = get_output_file_path(args.input, args.output, args.json)
    
    # Nicht-Aktivitätsdiagramme behandeln
    if diagram_type != DIAGRAM_TYPE_ACTIVITY:
        if diagram_type == DIAGRAM_TYPE_NOT_PLANTUML:
            print(f"Error: The file '{args.input}' does not appear to be a valid PlantUML file.")
        else:
            print(f"Error: The file '{args.input}' contains a {diagram_type} diagram. Currently only activity diagrams are supported.")
        sys.exit(1)

    # Prüfen, ob das Aktivitätsdiagramm gültig ist
    if not is_valid_activity_diagram(plantuml_content):
        print(f"Error: The file '{args.input}' does not contain a valid PlantUML activity diagram.")
        sys.exit(1)

    # Diagramm verarbeiten
    output_content, output_format = process_diagram(plantuml_content, args.json)
    if output_content is None:
        sys.exit(1)
        
    # Inhalt in Datei schreiben
    if write_output_file(output_content, output_file):
        print(f"{output_format} file successfully created: {output_file}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()