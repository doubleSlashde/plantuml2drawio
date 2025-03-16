#!/usr/bin/env python3
"""
Base-Processor-Modul für alle Diagramm-Prozessoren.
Dieses Modul definiert die Basis-Klassen und Schnittstellen, die alle Diagramm-Prozessoren implementieren sollten.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any


class DiagramNode:
    """Basisklasse für einen Knoten in einem Diagramm."""
    def __init__(self, id: str, label: str, shape: str, x: int = 0, y: int = 0, 
                 width: int = 120, height: int = 40):
        self.id = id
        self.label = label
        self.shape = shape
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class DiagramEdge:
    """Basisklasse für eine Kante in einem Diagramm."""
    def __init__(self, id: str, source: str, target: str, label: str = ""):
        self.id = id
        self.source = source
        self.target = target
        self.label = label


class BaseDiagramProcessor(ABC):
    """
    Abstrakte Basisklasse für alle Diagramm-Prozessoren.
    Jeder Diagramm-Prozessor muss diese Klasse erweitern und die abstrakten Methoden implementieren.
    """
    
    @staticmethod
    @abstractmethod
    def is_valid_diagram(content: str) -> bool:
        """
        Überprüft, ob der übergebene PlantUML-Inhalt ein gültiges Diagramm des entsprechenden Typs ist.
        
        Args:
            content: Der PlantUML-Inhalt als String
            
        Returns:
            bool: True, wenn es sich um ein gültiges Diagramm handelt, sonst False
        """
        pass
    
    @staticmethod
    @abstractmethod
    def parse_diagram(content: str) -> Tuple[List[DiagramNode], List[DiagramEdge]]:
        """
        Parst den PlantUML-Inhalt und erstellt daraus Knoten und Kanten.
        
        Args:
            content: Der PlantUML-Inhalt als String
            
        Returns:
            Tuple[List[DiagramNode], List[DiagramEdge]]: Eine Tuple mit der Liste der Knoten und Kanten
        """
        pass
    
    @staticmethod
    @abstractmethod
    def layout_diagram(nodes: List[DiagramNode], edges: List[DiagramEdge], 
                       **kwargs) -> Tuple[List[DiagramNode], List[DiagramEdge]]:
        """
        Berechnet das Layout des Diagramms.
        
        Args:
            nodes: Liste der Diagramm-Knoten
            edges: Liste der Diagramm-Kanten
            **kwargs: Zusätzliche Parameter für das Layout
            
        Returns:
            Tuple[List[DiagramNode], List[DiagramEdge]]: Eine Tuple mit den positionierten Knoten und Kanten
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_drawio_xml(nodes: List[DiagramNode], edges: List[DiagramEdge]) -> str:
        """
        Erstellt ein Draw.io-XML-Dokument aus den Knoten und Kanten.
        
        Args:
            nodes: Liste der Diagramm-Knoten
            edges: Liste der Diagramm-Kanten
            
        Returns:
            str: Das Draw.io-XML-Dokument als String
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_json(nodes: List[DiagramNode], edges: List[DiagramEdge]) -> str:
        """
        Erstellt eine JSON-Repräsentation des Diagramms.
        
        Args:
            nodes: Liste der Diagramm-Knoten
            edges: Liste der Diagramm-Kanten
            
        Returns:
            str: Die JSON-Repräsentation als String
        """
        pass 