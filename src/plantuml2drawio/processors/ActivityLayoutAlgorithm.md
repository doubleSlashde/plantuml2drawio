# Algorithmus zur Positionierung von Elementen in einem Aktivitätsdiagramm

Der Algorithmus positioniert Knoten eines Aktivitätsdiagramms rekursiv, wobei folgende Knotentypen behandelt werden:

- **Start- und Endknoten**
- **Aktivitätsknoten** (immer einen Eingang, genau einen Ausgang)
- **Bedingungsknoten** (zwei Ausgänge: „wahr" und „falsch")
- **Merge-Knoten** (zwei Eingänge)

Alle Knoten werden vertikal in gleichen Abständen angeordnet (von oben nach unten). Zusätzlich wird bei Bedingungen der falsche Pfad um einen festen horizontalen Offset verschoben. Wichtig ist, dass auch bei Bedingungen, die auf bereits verschobenen (falschen) Pfaden auftreten, der zusätzliche Offset kumulativ angewendet wird – und dass alle nachfolgenden Knoten, egal ob auf dem ursprünglich „richtigen" (vertikalen) Pfad oder auf einem falschen Pfad, stets mindestens den maximal erreichten Offset übernehmen.

---

### Parameter

- **verticalSpacing:** Fester vertikaler Abstand zwischen den Knoten.
- **horizontalOffset:** Fester horizontaler Versatz, der bei jedem Übergang in den falschen Pfad addiert wird.
- **currentOffset:** Lokaler Offset, der den kumulierten Versatz entlang des aktuellen Pfades angibt.
- **globalOffset:** Der bislang maximale Offset, der in falschen Pfaden gesetzt wurde und auch auf den „richtigen" (vertikalen) Pfad übernommen wird, um bereits verankerte falsche Pfade nicht zu "verrutschen".

---

### Pseudocode

```pseudo
function layout(node, baseX, currentY, currentOffset, globalOffset):
    // Positioniere den aktuellen Knoten:
    // Der x-Wert entspricht dem Basiswert plus dem maximalen Offset (currentOffset oder globalOffset)
    node.x = baseX + max(currentOffset, globalOffset)
    node.y = currentY

    // Bereite den nächsten vertikalen Startpunkt vor
    newY = currentY + verticalSpacing

    if node.type == 'Bedingung':
        // RICHTIGER Pfad: Der True-Ausgang folgt vertikal ohne zusätzlichen Offset.
        if node.trueSuccessor exists:
            layout(node.trueSuccessor, baseX, newY, currentOffset, globalOffset)

        // FALSCHER Pfad: Hier wird der currentOffset um den horizontalOffset erhöht.
        newFalseOffset = currentOffset + horizontalOffset
        // Aktualisiere globalOffset, sodass er den maximal erreichten Offset abbildet.
        newGlobalOffset = max(globalOffset, newFalseOffset)
        if node.falseSuccessor exists:
            layout(node.falseSuccessor, baseX, newY, newFalseOffset, newGlobalOffset)

    else if node.type == 'Aktivität' or node.type == 'Start' or node.type == 'Merge':
        // Diese Knoten haben einen einzigen Ausgang.
        if node.successor exists:
            layout(node.successor, baseX, newY, currentOffset, globalOffset)

    else if node.type == 'End':
        // Endknoten: Keine Nachfolger
        return
```

---

### Funktionsweise und Besonderheiten

1. **Start und Vertikale Platzierung:**
   Der Layout-Prozess beginnt mit dem Startknoten. Jeder Knoten wird so positioniert, dass seine x-Koordinate `baseX + max(currentOffset, globalOffset)` ist. Der y-Wert wird stets um den festen `verticalSpacing` erhöht.

2. **Bedingungsknoten:**
   - Beim **wahren Ausgang** (True-Pfad) bleibt der `currentOffset` unverändert – der Pfad verläuft vertikal.
   - Beim **falschen Ausgang** (False-Pfad) wird der `currentOffset` um `horizontalOffset` erhöht. Dieser neue Offset wird dann als Basis für alle Knoten in diesem Pfad verwendet.
   - Gleichzeitig wird der `globalOffset` aktualisiert, sodass auch Knoten, die anschließend auf einem "richtigen" (vertikalen) Pfad folgen, den maximal erreichten Offset übernehmen. Das ist entscheidend, um auch dann, wenn auf dem vertikalen Pfad wieder eine Bedingung auftritt, alle zuvor verschobenen falschen Pfade mitzuschieben.

3. **Konditionen auf falschen Pfaden:**
   Der Algorithmus behandelt Bedingungen auf falschen Pfaden genauso wie Bedingungen auf dem vertikalen Pfad. Das bedeutet:
   - Auch hier wird beim falschen Ausgang der `currentOffset` um den `horizontalOffset` erhöht und der `globalOffset` angepasst.
   - Somit wird sichergestellt, dass sich bei mehrfach verschachtelten Bedingungen die Verschiebung nach rechts stets kumulativ erhöht.

4. **Merge-Knoten:**
   Bei Merge-Knoten, die zwei Eingänge besitzen, kann es nötig sein, die x-Position anhand der x-Werte beider Eingänge zu berechnen (beispielsweise den maximalen Wert). Im obigen Pseudocode wird angenommen, dass der bereits übergebene Offset ausreichend ist; je nach konkreter Implementierung kann hier noch eine Zusammenführungslogik ergänzt werden.

---

### Beispielaufruf

Der Algorithmus wird mit dem Startknoten initialisiert, z. B.:

```pseudo
layout(startNode, 0, 0, 0, 0)
```

Dabei wird `baseX` als 0 gewählt und sowohl `currentOffset` als auch `globalOffset` starten bei 0.

---

### Zusammenfassung

- **Rekursives Layout:** Jeder Knoten wird unter Berücksichtigung von vertikalem Abstand und horizontalem Offset positioniert.
- **Bedingungen:**
  - Der True-Pfad bleibt vertikal, während der False-Pfad um einen festen horizontalen Versatz nach rechts verschoben wird.
  - Dieser Versatz wird kumulativ weitergegeben, sodass auch bei Bedingungen auf bereits falschen Pfaden alle nachfolgenden Knoten entsprechend verschoben werden.
- **globalOffset:** Er gewährleistet, dass alle Knoten – auch wenn sie später im vertikalen Pfad auftauchen – mindestens den maximal erreichten Offset übernehmen, um die Konsistenz des Layouts zu sichern.

Diese Beschreibung sollte alle geforderten Layout-Regeln und das Verhalten bei verschachtelten Bedingungen abdecken.
