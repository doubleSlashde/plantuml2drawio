import tkinter as tk
from tkinter import filedialog
import os
import tempfile
from p2dcore import parse_plantuml, create_drawio_xml
import tkinter.font as tkFont

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("plantuml to draw.io")
        self.root.geometry("600x400")  # Fenstergröße: 600x400

        # Konfiguriere das Hauptgrid: Spalte 1 (rechts) soll skalieren.
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Linker Bereich (Buttons und Copyright)
        self.left_frame = tk.Frame(root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # "Select File"-Button oben im linken Bereich
        self.file_button = tk.Button(self.left_frame, text="Open File", command=self.open_file)
        self.file_button.pack(side="top", fill="x", pady=(0, 5))
        
        # "Convert to draw.io"-Button direkt darunter
        self.convert_button = tk.Button(self.left_frame, text="Convert to Draw.io", command=self.convert_to_drawio)
        self.convert_button.pack(side="top", fill="x")
        
        # Ein expandierender Spacer, der den restlichen Platz einnimmt
        spacer = tk.Frame(self.left_frame)
        spacer.pack(fill="both", expand=True)
        
        # Copyright-Label am unteren Rand des linken Bereichs (© statt (c))
        copyright_label = tk.Label(
            self.left_frame,
            text="© 2025 doubleSlash.de"
        )
        copyright_label.pack(side="bottom")

        # Rechter Bereich (Dateiname + Text-Widget)
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        # Label über dem Text-Widget zur Anzeige des Dateinamens
        self.filename_label = tk.Label(self.right_frame, text="No file selected.", anchor="w")
        self.filename_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Text-Komponente zur Anzeige des Dateiinhalts
        self.text_widget = tk.Text(self.right_frame, wrap="word")
        self.text_widget.grid(row=1, column=0, sticky="nsew")
        
        # Konfiguration für das PlantUML-Highlighting: 
        # '@startuml' und '@enduml' in Weinrot (#800000)
        self.text_widget.tag_configure("plantuml", foreground="#800000")
        
        # Konfiguration für 'start' und 'stop': schwarz und fett
        default_font = tkFont.nametofont("TkDefaultFont")
        bold_font = default_font.copy()
        bold_font.configure(weight="bold")
        self.text_widget.tag_configure("startstop", foreground="#000000", font=bold_font)
        
        # Konfiguration für 'if', 'then', 'else' und 'endif': blau
        self.text_widget.tag_configure("ifthenelse", foreground="#0000FF")
        
        # Bind KeyRelease-Event, damit das Highlighting beim Bearbeiten aktualisiert wird
        self.text_widget.bind("<KeyRelease>", lambda event: self.highlight_plantuml())

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("PlantUML and Text Files", ("*.puml", "*.txt", "*.plantuml", "*.uml"))]
        )
        if file_path:
            base_name = os.path.basename(file_path)
            self.filename_label.config(text=f"Loaded file: {base_name}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, data)
                # Starte das Highlighting
                self.highlight_plantuml()
            except Exception as e:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, f"Error loading file:\n{e}")
        else:
            self.filename_label.config(text="No file selected.")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, "No file selected.")
            self.highlight_plantuml()
            
    def highlight_plantuml(self):
        """Markiert spezielle Schlüsselwörter im Text-Widget.
        
        - '@startuml' und '@enduml' in Weinrot (#800000)
        - 'start' und 'stop' in Schwarz und Fett
        - 'if', 'then', 'else' und 'endif' in Blau
        """
        # Entferne vorhandene Tags
        self.text_widget.tag_remove("plantuml", "1.0", tk.END)
        self.text_widget.tag_remove("ifthenelse", "1.0", tk.END)
        
        # Highlight für @startuml und @enduml
        patterns = ["@startuml", "@enduml","start", "stop"]
        for pattern in patterns:
            start_idx = "1.0"
            while True:
                pos = self.text_widget.search(pattern, start_idx, stopindex=tk.END)
                if not pos:
                    break
                end_pos = f"{pos}+{len(pattern)}c"
                self.text_widget.tag_add("plantuml", pos, end_pos)
                start_idx = end_pos

        for pattern in ["if", "then", "else", "endif"]:
            start_idx = "1.0"
            while True:
                pos = self.text_widget.search(pattern, start_idx, stopindex=tk.END)
                if not pos:
                    break
                end_pos = f"{pos}+{len(pattern)}c"
                self.text_widget.tag_add("ifthenelse", pos, end_pos)
                start_idx = end_pos

    def convert_to_drawio(self):
        # Inhalt der Text-Komponente (PlantUML-Code) abrufen
        plantuml_code = self.text_widget.get("1.0", tk.END)
        if not plantuml_code.strip():
            self.text_widget.insert(tk.END, "\nNo PlantUML code available for conversion.\n")
            return

        # Schreibe den Inhalt in eine temporäre Datei, da parse_plantuml() einen Dateinamen erwartet
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".puml", encoding="utf-8") as tmp:
            tmp.write(plantuml_code)
            tmp_filename = tmp.name

        try:
            # Parse PlantUML-Code, um ihn in Knoten und Kanten zu konvertieren
            nodes, edges = parse_plantuml(tmp_filename)
            # Generiere XML für draw.io
            drawio_xml = create_drawio_xml(nodes, edges)

            # Speicherdialog anzeigen, um den Speicherort für die draw.io-Datei auszuwählen
            save_path = filedialog.asksaveasfilename(
                title="Save Draw.io file",
                defaultextension=".drawio",
                filetypes=[("Draw.io Files", "*.drawio")]
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(drawio_xml)
                self.text_widget.insert(tk.END, f"\nDraw.io file created:\n{save_path}\n")
            else:
                self.text_widget.insert(tk.END, "\nSave cancelled.\n")
        except Exception as e:
            self.text_widget.insert(tk.END, f"\nError during conversion:\n{e}\n")
        finally:
            # Temporäre Datei löschen
            os.remove(tmp_filename)

def main():
    root = tk.Tk()
    import sys
    # Setze das Icon plattformübergreifend:
    if sys.platform.startswith('win'):
        # Unter Windows empfiehlt sich eine .ico-Datei
        try:
            root.iconbitmap("p2dapp_icon.ico")
        except Exception as e:
            print("Fehler beim Laden des Icons unter Windows:", e)
    else:
        # Unter macOS und Linux funktioniert eine .png-Datei in der Regel gut.
        try:
            icon = tk.PhotoImage(file="p2dapp_icon.png")
            root.iconphoto(False, icon)
        except Exception as e:
            print("Fehler beim Laden des Icons unter macOS/Linux:", e)

    app = FileSelectorApp(root)
    
    # Fenster in den Vordergrund bringen und den Fokus erzwingen
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 