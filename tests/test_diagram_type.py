#!/usr/bin/env python3
"""
Tests für die Diagrammtyperkennung.
"""
import unittest
import sys
import os

# Füge das src-Verzeichnis zum Pythonpfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plantuml2drawio.core import determine_plantuml_diagram_type
from src.plantuml2drawio.processors.activity_processor import is_valid_activity_diagram

class TestDiagramTypeDetection(unittest.TestCase):
    """Testklasse für die Diagrammtyperkennung."""

    def test_activity_diagram_detection(self):
        """Test, ob ein Aktivitätsdiagramm korrekt erkannt wird."""
        # Ein einfaches Aktivitätsdiagramm
        plantuml_content = """
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
        """
        
        diagram_type = determine_plantuml_diagram_type(plantuml_content)
        self.assertEqual(diagram_type, "activity")
        
        # Überprüfe auch die direkte is_valid_activity_diagram Funktion
        is_valid = is_valid_activity_diagram(plantuml_content)
        self.assertTrue(is_valid)

    def test_invalid_diagram(self):
        """Test, ob ein ungültiges Diagramm erkannt wird."""
        # Ein Text ohne gültigen PlantUML-Inhalt
        plantuml_content = """
        Dies ist kein gültiges PlantUML-Diagramm.
        Es enthält keine Start/End-Tags.
        """
        
        diagram_type = determine_plantuml_diagram_type(plantuml_content)
        self.assertEqual(diagram_type, "not_plantuml")
        
        # Überprüfe auch die direkte is_valid_activity_diagram Funktion
        is_valid = is_valid_activity_diagram(plantuml_content)
        self.assertFalse(is_valid)

    def test_empty_diagram(self):
        """Test, ob ein leeres Diagramm korrekt erkannt wird."""
        plantuml_content = ""
        
        diagram_type = determine_plantuml_diagram_type(plantuml_content)
        self.assertEqual(diagram_type, "not_plantuml")

    def test_minimal_activity_diagram(self):
        """Test, ob ein minimales Aktivitätsdiagramm erkannt wird."""
        plantuml_content = """
        @startuml
        start
        :Aktivität;
        stop
        @enduml
        """
        
        diagram_type = determine_plantuml_diagram_type(plantuml_content)
        self.assertEqual(diagram_type, "activity")
        
        is_valid = is_valid_activity_diagram(plantuml_content)
        self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main() 