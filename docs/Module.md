# Modulbeschreibungen

Dieser Abschnitt enthält detaillierte Informationen zu den einzelnen Modulen des PlantUML zu Draw.io Konverters.

## src/plantuml2drawio/core.py - Kernmodul

Das Kernmodul ist verantwortlich für:

- Verarbeitung von Kommandozeilenargumenten
- Erkennung des PlantUML-Diagrammtyps
- Koordination des Konvertierungsprozesses
- Auswahl des entsprechenden Prozessors für den erkannten Diagrammtyp
- Ausgabe des Ergebnisses im gewünschten Format

### Hauptfunktionen

- `determine_plantuml_diagram_type(content)`: Erkennt den Typ eines PlantUML-Diagramms
- `process_file(input_file, output_file, info_only)`: Steuert den Konvertierungsprozess
- `main()`: Einstiegspunkt für die Kommandozeilenverarbeitung

### Konstanten

| Konstante | Beschreibung |
|-----------|--------------|
| `OUTPUT_FORMAT_JSON` | Bezeichnung für JSON-Ausgabeformat |
| `OUTPUT_FORMAT_XML` | Bezeichnung für XML-Ausgabeformat |
| `DEFAULT_JSON_EXT` | Standarddateierweiterung für JSON-Ausgabe |
| `DEFAULT_DRAWIO_EXT` | Standarddateierweiterung für Draw.io-Ausgabe |
| `DIAGRAM_TYPE_ACTIVITY` | Bezeichnung für Aktivitätsdiagramme |
| `DIAGRAM_TYPE_NOT_PLANTUML` | Bezeichnung für ungültige PlantUML-Inhalte |

### Importierte Module

- `modules.activity_processor`: Funktionen für die Verarbeitung von Aktivitätsdiagrammen
- Standardbibliotheken: `sys`, `argparse`, `os`, `re`, `typing`

## modules/activity_processor.py - Aktivitätsdiagramm-Verarbeitung

Dieses Modul ist spezialisiert auf die Verarbeitung von PlantUML-Aktivitätsdiagrammen und enthält alle dafür notwendigen Funktionen.

### Klassen

| Klasse | Beschreibung |
|--------|--------------|
| `Node` | Repräsentiert einen Knoten im Diagramm mit Eigenschaften wie ID, Label, Form, Position und Größe |
| `Edge` | Repräsentiert eine Kante zwischen zwei Knoten im Diagramm mit Eigenschaften wie ID, Quell- und Zielknoten sowie Label |

### Hauptfunktionen

| Funktion | Beschreibung |
|----------|--------------|
| `is_valid_activity_diagram(plantuml_content)` | Überprüft, ob ein gültiges PlantUML-Aktivitätsdiagramm vorliegt |
| `parse_activity_diagram(plantuml_content)` | Analysiert das PlantUML-Aktivitätsdiagramm und erstellt Knoten- und Kantenlisten |
| `layout_activity_diagram(nodes, edges, ...)` | Berechnet ein optimales Layout für das Diagramm |
| `create_activity_drawio_xml(nodes, edges)` | Erzeugt XML im Draw.io-Format aus Knoten und Kanten |
| `create_json(nodes, edges)` | Erzeugt eine JSON-Repräsentation aus Knoten und Kanten |

### Importierte Module

- Standardbibliotheken: `re`, `xml.etree.ElementTree`, `sys`, `collections.defaultdict`, `json`

## src/plantuml2drawio/app.py - Grafische Benutzeroberfläche

Die GUI-Komponente bietet:

- Eine benutzerfreundliche Oberfläche für die Konvertierung
- Funktionen zum Laden und Speichern von Dateien
- Anzeige des erkannten Diagrammtyps
- Visualisierung des Konvertierungsprozesses

### Hauptklassen

- `FileSelectorApp`: Hauptklasse der Anwendung
- `PlantUMLEditor`: Editor für PlantUML-Code
- `StatusBar`: Statusleiste für Meldungen

### Hauptmethoden von FileSelectorApp

| Methode | Beschreibung |
|---------|--------------|
| `__init__(self, root)` | Initialisiert die GUI und ihre Komponenten |
| `create_menubar(self)` | Erstellt die Menüleiste |
| `show_about(self)` | Zeigt Informationen über die Anwendung an |
| `open_file(self)` | Öffnet eine PlantUML-Datei über einen Dateiauswahldialog |
| `update_text_and_button_state(self)` | Aktualisiert den Zustand der Schaltflächen basierend auf dem Inhalt |
| `apply_syntax_highlighting(self)` | Wendet Syntax-Highlighting auf den PlantUML-Code an |
| `convert_to_drawio(self)` | Konvertiert den aktuellen PlantUML-Code in das Draw.io-Format |

### Importierte Module

- `modules.activity_processor`: Funktionen für die Verarbeitung von Aktivitätsdiagrammen
- `customtkinter`: Erweitertes Tkinter für moderne GUI-Elemente
- Standardbibliotheken: `os`, `sys`, `tkinter`, `traceback`

## src/processors/base_processor.py - Basisklasse für Prozessoren

Diese Basisklasse definiert die Schnittstelle für alle Diagramm-Prozessoren:

- Abstrakte Methoden für die Verarbeitung verschiedener Diagrammtypen
- Gemeinsame Funktionalität für alle Prozessoren
- Basisklassen für Diagrammelemente (Knoten, Kanten)

## src/processors/activity_processor.py - Aktivitätsdiagramm-Prozessor

Spezialisiertes Modul für die Verarbeitung von Aktivitätsdiagrammen:

- Parsing von PlantUML-Aktivitätsdiagrammen
- Extraktion von Knoten und Kanten
- Layout-Berechnung
- Generierung des Draw.io-XML-Formats

### Hauptfunktionen

- `is_valid_activity_diagram(content)`: Prüft, ob es sich um ein gültiges Aktivitätsdiagramm handelt
- `parse_activity_diagram(content)`: Extrahiert Knoten und Kanten
- `layout_activity_diagram(nodes, edges)`: Berechnet das Layout
- `create_activity_drawio_xml(nodes, edges)`: Erzeugt das Draw.io-XML

## Modulinteraktionen

Der typische Ablauf einer Konvertierung:

1. **Eingabe**:
   - `core.py` wird mit Eingabe- und Ausgabeparametern aufgerufen
   - `app.py` zeigt die Benutzeroberfläche an

2. **Verarbeitung**:
   - `core.py` erkennt den Diagrammtyp
   - Der entsprechende Prozessor wird ausgewählt
   - Der Prozessor parst das Diagramm und berechnet das Layout
   - Der Prozessor generiert das Draw.io-XML

3. **Ausgabe**:
   - `core.py` oder `app.py` speichert das Ergebnis

## Erweiterung um neue Diagrammtypen

Um einen neuen Diagrammtyp zu unterstützen:

1. Erstellen eines neuen Prozessors in `src/processors/`, der von `BaseDiagramProcessor` erbt
2. Implementieren der abstrakten Methoden für den neuen Diagrammtyp
3. Aktualisieren von `core.py`, um das neue Modul für den entsprechenden Diagrammtyp zu verwenden

Dank der modularen Architektur sind keine größeren Änderungen am bestehenden Code nötig. 