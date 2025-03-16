#!/usr/bin/env python3
"""
Beispiel-Diagramme für Testzwecke.
"""

activity_diagram = """
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

sequence_diagram = """
@startuml
actor User
participant "Frontend" as FE
participant "Backend" as BE
database "Database" as DB

User -> FE: Benutzeraktion
activate FE
FE -> BE: API-Anfrage
activate BE
BE -> DB: Datenbankabfrage
activate DB
DB --> BE: Daten
deactivate DB
BE --> FE: Antwort
deactivate BE
FE --> User: Aktualisierte Anzeige
deactivate FE
@enduml
"""

class_diagram = """
@startuml
class User {
  +id: int
  +name: string
  +email: string
  +register(): void
  +login(): bool
}

class Product {
  +id: int
  +name: string
  +price: double
  +getDetails(): string
}

class Order {
  +id: int
  +userId: int
  +items: list
  +addItem(item: Product): void
  +calculateTotal(): double
}

User "1" -- "many" Order: places
Order "many" -- "many" Product: contains
@enduml
"""

usecase_diagram = """
@startuml
actor User
actor Admin

rectangle "Online Shop" {
  usecase "Anmelden" as UC1
  usecase "Produkte durchsuchen" as UC2
  usecase "Warenkorb verwalten" as UC3
  usecase "Bestellung aufgeben" as UC4
  usecase "Nutzer verwalten" as UC5
  usecase "Produkte verwalten" as UC6
}

User --> UC1
User --> UC2
User --> UC3
User --> UC4
Admin --> UC1
Admin --> UC5
Admin --> UC6
@enduml
"""

component_diagram = """
@startuml
package "Frontend" {
  [UI Components] as UI
  [State Management] as SM
}

package "Backend" {
  [API Gateway] as API
  [Authentication Service] as Auth
  [Product Service] as Prod
  [Order Service] as Order
}

database "Database" {
  [User DB] as UDB
  [Product DB] as PDB
  [Order DB] as ODB
}

UI --> SM
SM --> API
API --> Auth
API --> Prod
API --> Order
Auth --> UDB
Prod --> PDB
Order --> ODB
@enduml
"""

state_diagram = """
@startuml
[*] --> Idle

state Idle {
  [*] --> Ready
}

Idle --> Processing: Start Process
Processing --> Completed: Process Finished
Processing --> Error: Error Occurred
Completed --> Idle: Reset
Error --> Idle: Reset

state Processing {
  [*] --> Step1
  Step1 --> Step2
  Step2 --> Step3
  Step3 --> [*]
}
@enduml
"""

erd_diagram = """
@startuml
entity User {
  * id: int <<PK>>
  --
  * name: string
  * email: string
  password_hash: string
}

entity Product {
  * id: int <<PK>>
  --
  * name: string
  * price: double
  description: text
  category_id: int <<FK>>
}

entity Order {
  * id: int <<PK>>
  --
  * user_id: int <<FK>>
  * order_date: date
  total_amount: double
}

entity OrderItem {
  * id: int <<PK>>
  --
  * order_id: int <<FK>>
  * product_id: int <<FK>>
  * quantity: int
  price: double
}

User ||--o{ Order
Order ||--o{ OrderItem
Product ||--o{ OrderItem
@enduml
"""
