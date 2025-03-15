# PlantUML to Draw.io Converter

Ein Werkzeug zur Konvertierung von PlantUML-Diagrammen in das Draw.io-Format.

<p align="center">
  <img src="https://via.placeholder.com/700x200?text=PlantUML+to+Draw.io+Converter" alt="PlantUML to Draw.io Converter Logo"/>
</p>

## 📋 Übersicht

Dieses Projekt ermöglicht die Konvertierung von PlantUML-Diagrammen in das Draw.io-Format, wodurch eine nahtlose Integration von UML-Diagrammen in verschiedene Dokumentations- und Präsentationsworkflows ermöglicht wird. Der Konverter unterstützt derzeit Aktivitätsdiagramme und wird kontinuierlich um weitere Diagrammtypen erweitert.

## ✨ Hauptmerkmale

- 🔄 Konvertierung von PlantUML-Aktivitätsdiagrammen in das Draw.io-Format
- 🔍 Automatische Erkennung des PlantUML-Diagrammtyps
- 🖥️ Benutzerfreundliche GUI sowie Kommandozeilenschnittstelle
- 📐 Automatische Layout-Berechnung für optimale Diagrammdarstellung
- 🧩 Modularer Aufbau für einfache Erweiterbarkeit

## 🚀 Schnellstart

### Installation

```bash
# Repository klonen
git clone https://github.com/[username]/plantuml2drawio.git
cd plantuml2drawio

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Verwendung

#### Kommandozeile

```bash
python p2dcore.py --input diagrams/activity.puml --output diagrams/activity.drawio
```

#### Grafische Benutzeroberfläche

```bash
python p2dapp.py
```

## 📚 Dokumentation

Detaillierte Dokumentation ist im `docs`-Verzeichnis verfügbar:

- [Installation und Benutzung](Installation_und_Benutzung.md)
- [Arbeitsablauf](Arbeitsablauf.md)
- [Systemarchitektur](Systemarchitektur.md)
- [Erweiterungsmöglichkeiten](Erweiterungen.md)

## 🧪 Beispiele

### Aktivitätsdiagramm

**PlantUML-Eingabe**:
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

**Draw.io-Ausgabe**:

<p align="center">
  <img src="https://via.placeholder.com/500x300?text=Draw.io+Aktivitätsdiagramm" alt="Draw.io Aktivitätsdiagramm Beispiel"/>
</p>

## 🛠️ Technologiestack

- Python 3.6+
- tkinter für die GUI
- Reguläre Ausdrücke für das Parsing
- XML-Bibliotheken für die Draw.io-Generierung

## 🗺️ Roadmap

- [x] Unterstützung für Aktivitätsdiagramme
- [ ] Unterstützung für Sequenzdiagramme
- [ ] Unterstützung für Klassendiagramme
- [ ] Unterstützung für Komponentendiagramme
- [ ] Erweitertes Layout-Management
- [ ] Integration mit PlantUML-Server
- [ ] Web-Interface

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte lesen Sie unsere [Beitragsrichtlinien](CONTRIBUTING.md) für weitere Informationen.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.

## 🙏 Danksagungen

- [PlantUML](https://plantuml.com/) für die hervorragende UML-Diagramm-Syntax
- [Draw.io](https://www.draw.io/) für das offene XML-Format und die Diagramm-Bearbeitungsfunktionen

---

<p align="center">
  Erstellt mit ❤️ für UML-Enthusiasten und Softwareentwickler
</p> 