import tkinter as tk
from tkinter import filedialog
import os
import tempfile
from pumltodrawio import parse_plantuml, create_drawio_xml

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("plantuml to draw.io")
        self.root.geometry("600x400")  # Fenstergröße: 600x400

        # Konfiguration des Grids: Rechte Spalte (für Datei-Name und Textfeld) dehnt sich aus.
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Frame für die Buttons auf der linken Seite
        self.left_frame = tk.Frame(root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # "Datei auswählen"-Button im linken Frame, gleich breit
        self.file_button = tk.Button(self.left_frame, text="Datei auswählen", command=self.open_file)
        self.file_button.pack(fill='x', pady=(0, 5))

        # "Konvertiere nach draw.io"-Button direkt unter dem ersten Button, ebenfalls gleich breit
        self.convert_button = tk.Button(self.left_frame, text="Konvertiere nach draw.io", command=self.convert_to_drawio)
        self.convert_button.pack(fill='x')

        # Frame für den rechten Bereich (Dateiname + Textfeld)
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        # Label oberhalb des Textfelds zur Anzeige des Dateinamens
        self.filename_label = tk.Label(self.right_frame, text="Keine Datei ausgewählt.", anchor="w")
        self.filename_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Textkomponente zur Anzeige des Dateiinhalts
        self.text_widget = tk.Text(self.right_frame, wrap="word")
        self.text_widget.grid(row=1, column=0, sticky="nsew")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Wähle eine Datei aus",
            filetypes=[("PlantUML und Text Dateien", ("*.puml", "*.txt", "*.plantuml", "*.uml"))]
        )
        if file_path:
            base_name = os.path.basename(file_path)
            self.filename_label.config(text=f"Geladene Datei: {base_name}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, data)
            except Exception as e:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, f"Fehler beim Laden der Datei:\n{e}")
        else:
            self.filename_label.config(text="Keine Datei ausgewählt.")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, "Keine Datei ausgewählt.")

    def convert_to_drawio(self):
        # Inhalt des Textfelds abrufen (PlantUML-Code)
        plantuml_code = self.text_widget.get("1.0", tk.END)
        if not plantuml_code.strip():
            self.text_widget.insert(tk.END, "\nKein PlantUML-Code vorhanden, der konvertiert werden könnte.\n")
            return

        # In eine temporäre Datei schreiben, da parse_plantuml() einen Dateinamen erwartet
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".puml", encoding="utf-8") as tmp:
            tmp.write(plantuml_code)
            tmp_filename = tmp.name

        try:
            # PlantUML-Code parsen und in Knoten und Kanten umwandeln
            nodes, edges = parse_plantuml(tmp_filename)
            # XML für draw.io erzeugen
            drawio_xml = create_drawio_xml(nodes, edges)

            # Speicherdialog anzeigen, um Speicherort für die draw.io-Datei auszuwählen
            save_path = filedialog.asksaveasfilename(
                title="Speichere draw.io Datei",
                defaultextension=".xml",
                filetypes=[("XML Dateien", "*.xml")]
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(drawio_xml)
                self.text_widget.insert(tk.END, f"\nDraw.io Datei wurde erstellt:\n{save_path}\n")
            else:
                self.text_widget.insert(tk.END, "\nSpeichern abgebrochen.\n")
        except Exception as e:
            self.text_widget.insert(tk.END, f"\nFehler bei der Konvertierung:\n{e}\n")
        finally:
            # Temporäre Datei löschen, wenn sie nicht mehr benötigt wird
            os.remove(tmp_filename)

def main():
    root = tk.Tk()
    app = FileSelectorApp(root)
    
    # Fenster in den Vordergrund bringen und den Fokus erzwingen
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 