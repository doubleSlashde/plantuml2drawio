#!/usr/bin/env python3

from p2dcore import determine_plantuml_diagram_type

# Example PlantUML diagrams for testing

# Activity diagram
activity_diagram = """
@startuml
start
:Step 1;
if (Condition?) then (yes)
  :Step 2a;
else (no)
  :Step 2b;
endif
:Step 3;
stop
@enduml
"""

# Sequence diagram
sequence_diagram = """
@startuml
participant User
participant System

User -> System: Request data
activate System
System --> User: Return data
deactivate System
@enduml
"""

# Class diagram
class_diagram = """
@startuml
class User {
  +name: String
  +email: String
  +login(): void
}
class Admin extends User {
  +deleteUser(user: User): void
}
User <-- Admin
@enduml
"""

# Use case diagram
usecase_diagram = """
@startuml
actor User
actor Admin
usecase "Login" as UC1
usecase "View Profile" as UC2
User --> UC1
User --> UC2
Admin --> UC1
@enduml
"""

# Component diagram
component_diagram = """
@startuml
package "Web Application" {
  [Frontend]
  [Backend]
  [Database]
}
[Frontend] --> [Backend]
[Backend] --> [Database]
@enduml
"""

# State diagram
state_diagram = """
@startuml
[*] --> Start
Start --> Running
Running --> [*]
state Running {
  [*] --> Idle
  Idle --> Processing
  Processing --> Idle
}
@enduml
"""

# Entity-Relationship diagram
erd_diagram = """
@startuml
entity User {
  * id: number <<generated>>
  --
  * name: text
  * email: text
}
entity Order {
  * id: number <<generated>>
  --
  * date: date
  * status: text
}
User ||--o{ Order : places
@enduml
"""

# Dictionary of test diagrams
test_diagrams = {
    "activity": activity_diagram,
    "sequence": sequence_diagram,
    "class": class_diagram,
    "usecase": usecase_diagram,
    "component": component_diagram,
    "state": state_diagram,
    "erd": erd_diagram
}

# Test each diagram
for expected_type, content in test_diagrams.items():
    detected_type = determine_plantuml_diagram_type(content)
    result = "✓" if detected_type == expected_type else "✗"
    print(f"{result} {expected_type.ljust(10)} detected as: {detected_type}")

# Test invalid PlantUML
invalid_content = """
This is not a PlantUML diagram.
Just some random text.
"""
detected_type = determine_plantuml_diagram_type(invalid_content)
result = "✓" if detected_type == "not_plantuml" else "✗"
print(f"{result} {'invalid'.ljust(10)} detected as: {detected_type}") 