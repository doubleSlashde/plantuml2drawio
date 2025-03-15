# Arbeitsablauf

Dieses Dokument beschreibt den detaillierten Arbeitsablauf bei der Konvertierung eines PlantUML-Diagramms in das Draw.io-Format.

## Gesamtprozess

Der vollständige Prozess der Konvertierung umfasst die folgenden Hauptschritte:

```plantuml
@startuml Arbeitsablauf
start
:Einlesen des PlantUML-Codes;
:Erkennung des Diagrammtyps;
if (Unterstützter Diagrammtyp?) then (ja)
  if (Aktivitätsdiagramm?) then (ja)
    :Validierung des Aktivitätsdiagramms;
    if (Gültiges Diagramm?) then (ja)
      :Parsing des Aktivitätsdiagramms;
      :Berechnung des Layouts;
      if (JSON-Format gewünscht?) then (ja)
        :Erstellung des JSON-Outputs;
      else (nein)
        :Erstellung des Draw.io-XML;
      endif
      :Speichern der Ausgabedatei;
      :Erfolgreiche Konvertierung;
    else (nein)
      :Fehler: Ungültiges Aktivitätsdiagramm;
    endif
  else (nein)
    :Fehler: Diagrammtyp noch nicht unterstützt;
  endif
else (nein)
  :Fehler: Kein gültiger PlantUML-Code;
endif
stop
@enduml
```

## Detaillierte Beschreibung der Schritte

### 1. Einlesen des PlantUML-Codes

- **Verantwortliches Modul:** p2dcore.py
- **Funktion:** `read_plantuml_file(file_path)`
- **Beschreibung:** 
  - Die Eingabedatei wird geöffnet und der Inhalt als Text gelesen
  - Der Unicode-Zeichensatz (UTF-8) wird verwendet, um auch Sonderzeichen zu unterstützen
  - Bei Fehlern während des Lesevorgangs wird eine entsprechende Fehlermeldung ausgegeben

### 2. Erkennung des Diagrammtyps

- **Verantwortliches Modul:** p2dcore.py
- **Funktion:** `determine_plantuml_diagram_type(plantuml_content)`
- **Beschreibung:**
  - Der PlantUML-Code wird analysiert, um den Diagrammtyp zu bestimmen
  - Verschiedene Indikatoren im Code werden geprüft (Keywords, Syntax-Elemente, etc.)
  - Der Diagrammtyp mit der höchsten Übereinstimmung wird zurückgegeben
  - Bei fehlendem @startuml/@enduml wird "not_plantuml" zurückgegeben

### 3. Validierung des Aktivitätsdiagramms

- **Verantwortliches Modul:** modules/activity_processor.py
- **Funktion:** `is_valid_activity_diagram(plantuml_content)`
- **Beschreibung:**
  - Überprüfung auf erforderliche Elemente eines Aktivitätsdiagramms
  - Prüfung auf PlantUML-Markierungen (@startuml, @enduml)
  - Prüfung auf grundlegende Elemente (start, stop)
  - Prüfung auf Aktivitätszeilen oder if-Blöcke

### 4. Parsing des Aktivitätsdiagramms

- **Verantwortliches Modul:** modules/activity_processor.py
- **Funktion:** `parse_activity_diagram(plantuml_content)`
- **Beschreibung:**
  - Zeilenweise Analyse des PlantUML-Codes
  - Identifikation von Knoten (Start, Stop, Aktivitäten, Bedingungen)
  - Identifikation von Kanten (Verbindungen zwischen Knoten)
  - Erstellung einer internen Repräsentation als Listen von Node- und Edge-Objekten

### 5. Berechnung des Layouts

- **Verantwortliches Modul:** modules/activity_processor.py
- **Funktion:** `layout_activity_diagram(nodes, edges, ...)`
- **Beschreibung:**
  - Berechnung der optimalen Positionen für alle Knoten
  - Verwendung eines rekursiven Tiefensuchalgorithmus (DFS)
  - Zuweisung von Koordinaten basierend auf der Hierarchie im Diagramm
  - Spezialbehandlung für Verzweigungs- und Vereinigungsknoten

### 6. Erstellung der Ausgabe

- **Verantwortliches Modul:** modules/activity_processor.py
- **Funktionen:** 
  - `create_activity_drawio_xml(nodes, edges)` für Draw.io-XML
  - `create_json(nodes, edges)` für JSON-Format
- **Beschreibung:**
  - Bei XML: Erstellung einer XML-Struktur nach dem Draw.io-Format mit den korrekten Stilen und Eigenschaften
  - Bei JSON: Erstellung einer JSON-Repräsentation der Knoten und Kanten
  - Kodierung als UTF-8 für Unterstützung von Sonderzeichen

### 7. Speichern der Ausgabedatei

- **Verantwortliches Modul:** p2dcore.py oder p2dapp.py (je nach Schnittstelle)
- **Funktion:** 
  - CLI: `write_output_file(content, file_path)`
  - GUI: Dateiauswahldialog in `convert_to_drawio()`
- **Beschreibung:**
  - Schreiben des generierten Inhalts in eine Datei
  - Bei CLI: Verwendung des angegebenen oder automatisch bestimmten Dateinamens
  - Bei GUI: Anzeigen eines Speicherdialogs für den Benutzer

## Fehlerbehandlung

Das System beinhaltet mehrere Ebenen der Fehlerbehandlung:

1. **Frühe Validierung:**
   - Überprüfung auf gültigen PlantUML-Code
   - Identifikation des Diagrammtyps
   - Spezifische Validierung für Aktivitätsdiagramme

2. **Strukturierte Ausnahmebehandlung:**
   - Try-Except-Blöcke für alle kritischen Operationen
   - Detaillierte Fehlermeldungen für die verschiedenen Verarbeitungsstufen
   - Unterscheidung zwischen E/A-Fehlern und Verarbeitungsfehlern

3. **Benutzerrückmeldung:**
   - CLI: Aussagekräftige Fehlermeldungen auf der Konsole
   - GUI: Statusmeldungen in der Benutzeroberfläche

## Beispiel

Ein einfaches Beispiel für die Konvertierung eines Aktivitätsdiagramms:

```plantuml
@startuml
start
:Schritt 1;
if (Bedingung?) then (ja)
  :Schritt 2a;
else (nein)
  :Schritt 2b;
endif
:Schritt 3;
stop
@enduml
```

Wird konvertiert in eine Draw.io-XML-Datei, die in Draw.io geöffnet werden kann und das Diagramm mit denselben Elementen und Verbindungen darstellt, jedoch mit dem Draw.io-eigenen Darstellungsstil. 