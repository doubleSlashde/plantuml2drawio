"""Processors package for converting different types of PlantUML diagrams."""

from plantuml2drawio.config import DIAGRAM_TYPE_ACTIVITY
from plantuml2drawio.processors.activity_processor import \
    ActivityDiagramProcessor
from plantuml2drawio.processors.base_processor import ProcessorRegistry

# Register all available processors
ProcessorRegistry.register(DIAGRAM_TYPE_ACTIVITY, ActivityDiagramProcessor)

# Export publicly useful functionality
__all__ = ["ProcessorRegistry"]
