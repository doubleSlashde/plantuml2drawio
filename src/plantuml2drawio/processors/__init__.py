"""Processors package for converting different types of PlantUML diagrams."""

# Try to import from installed package or development path
try:
    # Installed package path
    from plantuml2drawio.config import DIAGRAM_TYPE_ACTIVITY
    from plantuml2drawio.processors.activity_processor import \
        ActivityDiagramProcessor
    from plantuml2drawio.processors.base_processor import ProcessorRegistry
except ImportError:
    # Development path
    from src.plantuml2drawio.config import DIAGRAM_TYPE_ACTIVITY
    from src.plantuml2drawio.processors.activity_processor import \
        ActivityDiagramProcessor
    from src.plantuml2drawio.processors.base_processor import ProcessorRegistry

# Register all available processors
ProcessorRegistry.register(DIAGRAM_TYPE_ACTIVITY, ActivityDiagramProcessor)

# Export publicly useful functionality
__all__ = ["ProcessorRegistry"]
