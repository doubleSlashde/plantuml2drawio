# Installation und Benutzung

Dieses Dokument beschreibt die Installation und Benutzung des PlantUML zu Draw.io Konverters.

## Installation

### Voraussetzungen

- Python 3.6 oder höher
- pip (Python-Paketmanager)

### Installation von GitHub

1. Klonen Sie das Repository:
   ```bash
   git clone https://github.com/[username]/plantuml2drawio.git
   cd plantuml2drawio
   ```

2. Installieren Sie die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

### Installation als Python-Paket (optional)

Sobald das Paket auf PyPI verfügbar ist:

```bash
pip install plantuml2drawio
```

## Benutzung

Der Konverter kann sowohl über die Kommandozeile als auch über die grafische Benutzeroberfläche verwendet werden.

### Kommandozeile

#### Grundlegende Verwendung

```bash
python p2dcore.py --input <eingabedatei.puml> --output <ausgabedatei.drawio>
```

Beispiel:
```bash
python p2dcore.py --input diagrams/activity.puml --output diagrams/activity.drawio
```

#### Nur Diagrammtyp anzeigen

```bash
python p2dcore.py --input <eingabedatei.puml> --info
```

Beispiel:
```bash
python p2dcore.py --input diagrams/activity.puml --info
```

#### Hilfe anzeigen

```bash
python p2dcore.py --help
```

### Grafische Benutzeroberfläche

Starten Sie die grafische Benutzeroberfläche mit:

```bash
python p2dapp.py
```

#### Verwendung der GUI

1. **PlantUML-Code eingeben**
   - Geben Sie den PlantUML-Code direkt in das Textfeld ein, oder
   - Laden Sie eine PlantUML-Datei über "Datei öffnen"

2. **Konvertierung starten**
   - Klicken Sie auf "Konvertieren"
   - Der erkannte Diagrammtyp wird angezeigt
   - Bei Erfolg wird die Draw.io-XML generiert

3. **Ergebnis speichern**
   - Klicken Sie auf "Speichern" oder "Speichern unter"
   - Wählen Sie einen Dateinamen mit der Endung .drawio

## Unterstützte Diagrammtypen

Derzeit werden folgende PlantUML-Diagrammtypen unterstützt:

| Diagrammtyp       | Unterstützung |
|-------------------|---------------|
| Aktivitätsdiagramm| ✓ Vollständig |
| Sequenzdiagramm   | ✗ Geplant     |
| Klassendiagramm   | ✗ Geplant     |
| Komponentendiagramm| ✗ Geplant     |
| Zustandsdiagramm  | ✗ Geplant     |
| ER-Diagramm       | ✗ Geplant     |

## Beispiele

### Aktivitätsdiagramm

**PlantUML-Eingabe**:
```
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

**Resultat**: Ein in Draw.io importierbares Aktivitätsdiagramm mit entsprechenden Elementen.

## Fehlerbehandlung

### Häufige Fehler

1. **Ungültiger PlantUML-Code**:
   - Fehlermeldung: "Ungültiger PlantUML-Code"
   - Lösung: Überprüfen Sie die Syntax und stellen Sie sicher, dass der Code mit @startuml beginnt und mit @enduml endet.

2. **Nicht unterstützter Diagrammtyp**:
   - Fehlermeldung: "Nicht unterstützter Diagrammtyp"
   - Lösung: Verwenden Sie einen der unterstützten Diagrammtypen oder warten Sie auf eine zukünftige Version.

3. **Datei nicht gefunden**:
   - Fehlermeldung: "Datei nicht gefunden"
   - Lösung: Überprüfen Sie den Pfad zur Eingabedatei.

### Logs

Bei Problemen können Sie detailliertere Logs aktivieren:

```bash
python p2dcore.py --input <eingabedatei.puml> --output <ausgabedatei.drawio> --debug
```

## Tipps und Tricks

1. **Komplexe Aktivitätsdiagramme**:
   - Teilen Sie komplexe Diagramme in kleinere Teile auf
   - Verwenden Sie eindeutige Bezeichner für Aktivitäten und Entscheidungen

2. **Kompatibilität mit Draw.io**:
   - Die erzeugten .drawio-Dateien können in allen Draw.io-kompatiblen Tools geöffnet werden
   - Dies schließt die Online-Version, Desktop-Anwendung und die VSCode-Erweiterung ein

3. **Integration in Workflows**:
   - Sie können die Konvertierung in CI/CD-Pipelines integrieren
   - Beispiel für ein Git-Hook-Skript zur automatischen Konvertierung beim Commit

## Support

Bei Fragen oder Problemen:

1. Prüfen Sie die FAQ im [Wiki](https://github.com/[username]/plantuml2drawio/wiki)
2. Eröffnen Sie ein [GitHub Issue](https://github.com/[username]/plantuml2drawio/issues)
3. Kontaktieren Sie den Entwickler: [email@example.com] 