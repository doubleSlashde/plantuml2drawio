# Modulbeschreibungen

Dieser Abschnitt enthält detaillierte Informationen zu den einzelnen Modulen des PlantUML zu Draw.io Konverters.

## p2dcore.py - Kernmodul

Das Kernmodul orchestriert den gesamten Konvertierungsprozess und stellt die Hauptfunktionalität des Systems bereit.

### Hauptfunktionen

| Funktion | Beschreibung |
|----------|--------------|
| `determine_plantuml_diagram_type(plantuml_content)` | Analysiert PlantUML-Code und identifiziert den Diagrammtyp (Aktivitätsdiagramm, Sequenzdiagramm, etc.) |
| `process_diagram(plantuml_content, output_json)` | Verarbeitet den PlantUML-Inhalt und erzeugt XML oder JSON |
| `read_plantuml_file(file_path)` | Liest eine PlantUML-Datei ein |
| `write_output_file(content, file_path)` | Schreibt den konvertierten Inhalt in eine Datei |
| `get_output_file_path(input_file, output_file, is_json)` | Bestimmt den Pfad für die Ausgabedatei |
| `handle_info_request(diagram_type)` | Zeigt Informationen zum erkannten Diagrammtyp an |
| `main()` | Hauptfunktion für die Kommandozeilenschnittstelle |

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

## p2dapp.py - Grafische Benutzeroberfläche

Dieses Modul implementiert die grafische Benutzeroberfläche für den Konverter, basierend auf customtkinter.

### Klassen

| Klasse | Beschreibung |
|--------|--------------|
| `FileSelectorApp` | Hauptklasse für die GUI mit Methoden für Dateioperationen, Benutzerinteraktionen und Konvertierung |

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

## Zusammenspiel der Module

1. **Ablauf bei CLI-Nutzung**:
   - `p2dcore.py` wird mit Eingabe- und Ausgabeparametern aufgerufen
   - Die Hauptfunktion liest die Datei und bestimmt den Diagrammtyp
   - Bei Aktivitätsdiagrammen werden die entsprechenden Funktionen aus `activity_processor.py` aufgerufen
   - Das Ergebnis wird in die angegebene Ausgabedatei geschrieben

2. **Ablauf bei GUI-Nutzung**:
   - `p2dapp.py` zeigt die Benutzeroberfläche an
   - Der Benutzer lädt eine Datei oder gibt PlantUML-Code direkt ein
   - Beim Drücken des Konvertierungsbuttons werden die entsprechenden Funktionen aus `activity_processor.py` aufgerufen
   - Das Ergebnis wird in einer vom Benutzer gewählten Datei gespeichert

## Erweiterungspunkte

Für die Unterstützung weiterer Diagrammtypen würden folgende Schritte erforderlich sein:

1. Erstellen eines neuen spezialisierten Moduls (z.B. `modules/sequence_processor.py`)
2. Implementieren der entsprechenden Funktionen (Validierung, Parsing, Layout, XML-Generierung)
3. Aktualisieren von `p2dcore.py`, um das neue Modul für den entsprechenden Diagrammtyp zu verwenden

Dank der modularen Architektur sind keine größeren Änderungen am bestehenden Code nötig. 