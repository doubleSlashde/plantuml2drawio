#!/usr/bin/env python3
"""Configuration module for plantuml2drawio.

Contains configuration parameters and constants for the entire project.
"""

# Version information
VERSION = "1.2.0"
VERSION_DATE = "2025-03-16"

# File formats and extensions
DEFAULT_JSON_EXT = ".json"
DEFAULT_DRAWIO_EXT = ".drawio"

# Output formats
OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_XML = "Draw.io XML"

# Diagram types
DIAGRAM_TYPE_ACTIVITY = "activity"
DIAGRAM_TYPE_SEQUENCE = "sequence"
DIAGRAM_TYPE_CLASS = "class"
DIAGRAM_TYPE_COMPONENT = "component"
DIAGRAM_TYPE_USECASE = "usecase"
DIAGRAM_TYPE_UNKNOWN = "unknown"

# Layout settings
DEFAULT_VERTICAL_SPACING = 100
DEFAULT_HORIZONTAL_SPACING = 200
DEFAULT_START_X = 60
DEFAULT_START_Y = 60

# Application settings
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_TITLE = "PlantUML zu Draw.io Konverter"

# Resources
# Icon path without extension, will be added based on platform
ICON_PATH = "resources/icons/p2d_icon"

# Available processors
AVAILABLE_PROCESSORS = {
    DIAGRAM_TYPE_ACTIVITY: (
        "plantuml2drawio.processors.activity_processor." "ActivityDiagramProcessor"
    )
}

# Debug settings
DEBUG = False

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
