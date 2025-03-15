# Systemübersicht

## Zweck und Funktionalität

Der PlantUML zu Draw.io Konverter ermöglicht die Umwandlung von PlantUML-Diagrammen in das Format von Draw.io. Dies ist besonders nützlich, wenn Benutzer ihre Diagramme in einer textbasierten Umgebung mit PlantUML erstellen, aber später in Draw.io weiterbearbeiten möchten, um von den visuellen Bearbeitungsmöglichkeiten zu profitieren.

## Architektur

Die Anwendung ist modular aufgebaut und folgt dem Prinzip der Trennung von Verantwortlichkeiten. Die wichtigsten Komponenten sind:

1. **Kernmodul (p2dcore.py)**: 
   - Hauptmodul, das die Diagrammtyperkennung und die Orchestrierung des Konvertierungsprozesses übernimmt
   - Bietet eine Kommandozeilenschnittstelle zur direkten Verwendung
   - Implementiert die Logik zur Erkennung verschiedener PlantUML-Diagrammtypen

2. **Aktivitätsdiagramm-Modul (modules/activity_processor.py)**:
   - Spezialisiertes Modul für die Verarbeitung von PlantUML-Aktivitätsdiagrammen
   - Enthält Funktionen zur Validierung, Parsing, Layout und Konvertierung von Aktivitätsdiagrammen
   - Separiert, um die Erweiterbarkeit für andere Diagrammtypen zu gewährleisten

3. **Benutzeroberfläche (p2dapp.py)**:
   - Graphische Benutzeroberfläche (GUI) für den Konverter
   - Ermöglicht das Laden, Bearbeiten und Konvertieren von PlantUML-Diagrammen
   - Bietet Syntax-Highlighting für PlantUML-Code

## Arbeitsweise

Der Konvertierungsprozess durchläuft folgende Schritte:

1. **Diagrammtyperkennung**: Die Eingangs-PlantUML-Datei wird analysiert, um den Diagrammtyp zu bestimmen.
2. **Validierung**: Es wird überprüft, ob das Diagramm gültig ist und dem unterstützten Format entspricht.
3. **Parsing**: Das PlantUML-Diagramm wird in eine interne Repräsentation aus Knoten und Kanten umgewandelt.
4. **Layout-Berechnung**: Die Positionen und Größen der Knoten werden optimiert, um ein ästhetisches Diagramm zu erzeugen.
5. **XML/JSON-Generierung**: Die interne Repräsentation wird in das Draw.io-XML-Format oder optional in JSON konvertiert.
6. **Ausgabe**: Das Ergebnis wird in eine Datei geschrieben oder in der GUI angezeigt.

## Schnittstellen

- **Kommandozeilenschnittstelle (CLI)**: Ermöglicht die Steuerung und Automatisierung des Konvertierungsprozesses.
- **Grafische Benutzeroberfläche (GUI)**: Bietet eine benutzerfreundliche Oberfläche für den interaktiven Einsatz.
- **Modulare Programmierschnittstelle (API)**: Ermöglicht die Einbindung der Konvertierungsfunktionen in andere Anwendungen.

## Zukunft und Erweiterbarkeit

Das System wurde mit Blick auf Erweiterbarkeit entworfen. Aktuell werden Aktivitätsdiagramme unterstützt, aber die modulare Struktur erleichtert die Implementierung weiterer PlantUML-Diagrammtypen wie:

- Sequenzdiagramme
- Klassendiagramme
- Komponentendiagramme
- Zustandsdiagramme
- ER-Diagramme

Jeder neue Diagrammtyp kann als separates Modul implementiert werden, ohne den bestehenden Code zu beeinträchtigen. 