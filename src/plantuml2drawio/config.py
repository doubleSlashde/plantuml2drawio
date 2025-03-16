#!/usr/bin/env python3
"""
Konfigurationsmodul für plantuml2drawio.
Enthält Konfigurationsparameter und Konstanten für das gesamte Projekt.
"""

# Versionsinformationen
VERSION = "1.1.0"
VERSION_DATE = "2024-03-15"

# Dateiformate und Erweiterungen
DEFAULT_JSON_EXT = ".json"
DEFAULT_DRAWIO_EXT = ".drawio"

# Ausgabeformate
OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_XML = "Draw.io XML"

# Diagrammtypen
DIAGRAM_TYPE_ACTIVITY = "activity"
DIAGRAM_TYPE_SEQUENCE = "sequence"
DIAGRAM_TYPE_CLASS = "class"
DIAGRAM_TYPE_COMPONENT = "component"
DIAGRAM_TYPE_USECASE = "usecase"
DIAGRAM_TYPE_UNKNOWN = "unknown"

# Layout-Einstellungen
DEFAULT_VERTICAL_SPACING = 100
DEFAULT_HORIZONTAL_SPACING = 200
DEFAULT_START_X = 60
DEFAULT_START_Y = 60

# Anwendungseinstellungen
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_TITLE = "PlantUML zu Draw.io Konverter"

# Ressourcen
ICON_PATH = "resources/icons/p2d_icon"  # Ohne Dateiendung, wird je nach Plattform ergänzt

# Verfügbare Prozessoren
AVAILABLE_PROCESSORS = {
    DIAGRAM_TYPE_ACTIVITY: "plantuml2drawio.processors.activity_processor.ActivityDiagramProcessor"
}

# Debug-Einstellungen
DEBUG = False 