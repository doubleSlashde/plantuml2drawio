# Komponentendiagramm

Das folgende Komponentendiagramm zeigt die Hauptmodule des PlantUML zu Draw.io Konverters und ihre Abhängigkeiten:

```plantuml
@startuml Komponentendiagramm

!define LIGHTBLUE
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

' Komponenten
component "p2dcore.py" as core {
  component "Diagrammtyperkennung" as typeDetection
  component "Prozesssteuerung" as processControl
  component "CLI" as cli
}

component "modules/activity_processor.py" as activity {
  component "Aktivitätsdiagramm Validierung" as activityValidation
  component "Parsing" as activityParsing
  component "Layout" as activityLayout
  component "XML/JSON Generierung" as activityExport
}

component "p2dapp.py" as gui {
  component "GUI" as guiComponent
  component "Syntax-Highlighting" as syntaxHighlight
  component "Dateihandling" as fileHandling
}

' Externe Komponenten/Abhängigkeiten
component "customtkinter" as ctk
component "Re (Regex)" as regex
component "XML ElementTree" as xml
component "JSON" as json
component "System (os, sys)" as system

' Abhängigkeiten zwischen Hauptkomponenten
core --> activity : importiert
gui --> activity : importiert

' Interne Abhängigkeiten
typeDetection --> processControl
processControl --> cli
activityValidation --> activityParsing
activityParsing --> activityLayout
activityLayout --> activityExport
guiComponent --> syntaxHighlight
guiComponent --> fileHandling

' Abhängigkeiten zu externen Komponenten
core --> regex : verwendet
core --> system : verwendet
activity --> regex : verwendet
activity --> xml : verwendet
activity --> json : verwendet
activity --> system : verwendet
gui --> ctk : verwendet
gui --> system : verwendet

@enduml
```

## Beschreibung der Komponenten

### Hauptmodule

1. **p2dcore.py**
   - **Diagrammtyperkennung**: Analysiert PlantUML-Code, um den Diagrammtyp zu identifizieren
   - **Prozesssteuerung**: Koordiniert den Konvertierungsprozess
   - **CLI**: Stellt eine Kommandozeilenschnittstelle bereit

2. **modules/activity_processor.py**
   - **Aktivitätsdiagramm Validierung**: Prüft, ob ein gültiges Aktivitätsdiagramm vorliegt
   - **Parsing**: Wandelt PlantUML-Code in eine interne Datenstruktur um
   - **Layout**: Berechnet optimale Positionen für Diagrammelemente
   - **XML/JSON Generierung**: Erzeugt DrawIO-XML oder JSON aus der internen Datenstruktur

3. **p2dapp.py**
   - **GUI**: Grafische Benutzeroberfläche
   - **Syntax-Highlighting**: Farbliche Hervorhebung von PlantUML-Code
   - **Dateihandling**: Funktionen zum Laden und Speichern von Dateien

### Externe Abhängigkeiten

- **customtkinter**: Erweitertes Tkinter-Framework für moderne GUI-Elemente
- **Re (Regex)**: Reguläre Ausdrücke für Parsing und Texterkennung
- **XML ElementTree**: XML-Verarbeitung für DrawIO-Ausgabe
- **JSON**: JSON-Verarbeitung für alternative Ausgabeformate
- **System (os, sys)**: Betriebssystem-Interaktion und Programmverwaltung

## Modulare Architektur

Das Diagramm veranschaulicht die klare Trennung der Verantwortlichkeiten zwischen den Modulen:

- **p2dcore.py** übernimmt die Koordination und generische Funktionalität
- **activity_processor.py** konzentriert sich ausschließlich auf Aktivitätsdiagramme
- **p2dapp.py** behandelt nur UI-bezogene Aspekte

Diese Architektur erleichtert die zukünftige Erweiterung um weitere Diagrammtypen. Neue Prozessoren können als separate Module hinzugefügt werden, ohne bestehenden Code zu verändern. 