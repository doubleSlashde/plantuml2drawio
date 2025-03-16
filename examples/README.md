# PlantUML zu Draw.io Beispiele

Dieses Verzeichnis enthält Beispiel-PlantUML-Diagramme, die mit dem plantuml2drawio-Konverter in das Draw.io-Format konvertiert werden können.

## Aktivitätsdiagramme

Das Verzeichnis `activity_examples` enthält Beispiele für PlantUML-Aktivitätsdiagramme:

- `simple_activity.puml`: Ein einfaches Aktivitätsdiagramm mit Verzweigungen und Flusssteuerung

## Verwendung der Beispiele

Sie können diese Beispiele wie folgt mit dem Konverter verwenden:

### Mit der Kommandozeile:

```bash
# Verwenden des CLI-Tools
./p2d-cli --input examples/activity_examples/simple_activity.puml --output examples/activity_examples/simple_activity.drawio
```

### Mit der grafischen Benutzeroberfläche:

1. Starten Sie die Anwendung mit `./p2d-gui`
2. Öffnen Sie eine der Beispiel-Dateien über die GUI
3. Konvertieren Sie das Diagramm mit der Schaltfläche "Konvertieren"
4. Speichern Sie das Ergebnis

## Eigene Beispiele hinzufügen

Fügen Sie Ihre eigenen Beispiele in die entsprechenden Unterverzeichnisse ein und verwenden Sie sie als Referenz für Ihre eigenen Diagramme.

Für weitere Diagrammtypen können neue Unterverzeichnisse erstellt werden, sobald weitere Diagrammtypen vom Konverter unterstützt werden.
