#!/usr/bin/env python3
import os
import sys

# Importiere die Version aus der config.py
from plantuml2drawio.config import VERSION, VERSION_DATE
# Importiere die Funktion aus dem neuen Modul mit dem neuen Namen
from plantuml2drawio.processors.activity_processor import \
    is_valid_activity_diagram


class FileSelectorApp:
    def __init__(self, root):
        # Verzögerter Import von customtkinter innerhalb der Klasse
        import customtkinter as ctk

        self.ctk = ctk

        self.root = root
        self.root.title("PlantUML zu Draw.io Konverter")
        self.root.geometry("800x600")  # Larger window for better overview

        # Set appearance mode and default color theme
        ctk.set_appearance_mode("System")  # "System", "Dark" oder "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

        # Create menubar
        self.create_menubar()

        # Configure main grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)  # Nur die Text-Widget-Zeile soll wachsen

        # Row 0: Combined filename and diagram type label
        self.filename_label = ctk.CTkLabel(
            self.root,
            text="Keine Datei ausgewählt | Diagramm-Typ: -",
            anchor="w",
            font=("Arial", 16),
        )
        self.filename_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Row 1: Horizontal button frame
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=50)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.button_frame.grid_propagate(False)  # Prevent frame from shrinking
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        # "Open File" button on the left
        self.file_button = ctk.CTkButton(
            self.button_frame,
            text="PlantUML-Datei öffnen",
            command=self.open_file,
            font=("Arial", 14, "bold"),
            width=180,  # Increased width to accommodate longer text
            height=40,
            corner_radius=50,
            fg_color="#00759e",
        )
        self.file_button.grid(row=0, column=0, sticky="w")

        # Spacer in the middle
        spacer = ctk.CTkLabel(self.button_frame, text="")
        spacer.grid(row=0, column=1, sticky="ew")

        # "Convert to Draw.io" button on the right;
        # initially disabled
        self.convert_button = ctk.CTkButton(
            self.button_frame,
            text="Nach Draw.io konvertieren",
            command=self.convert_to_drawio,
            state="disabled",
            font=("Arial", 14, "bold"),
            width=200,
            height=40,
            corner_radius=50,
            fg_color="#00759e",
        )
        self.convert_button.grid(row=0, column=2, sticky="e")

        # Row 2: Message label
        self.message_label = ctk.CTkLabel(
            self.root,
            text="",
            anchor="w",
            height=30,
            font=("Arial", 14),
            fg_color="#f0f0f0",  # Light gray background
            corner_radius=5,
        )
        self.message_label.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Row 3: Main frame for the text widget
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Text widget to display file contents
        self.text_widget = ctk.CTkTextbox(
            self.main_frame, wrap="word", font=("Courier New", 16)
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")

        # Farbdefinitionen für das Syntax-Highlighting
        # Zugriff auf das zugrundeliegende Tkinter-Text-Widget
        self.tk_text = self.text_widget._textbox
        # Setze alle Farben zunächst auf Dunkelgrau (statt Schwarz) für den normalen Text
        self.tk_text.configure(foreground="#444444")  # Dunkelgrau als Standardfarbe
        self.tk_text.tag_configure(
            "keyword", foreground="#FF00FF"
        )  # Magenta für Schlüsselwörter
        self.tk_text.tag_configure(
            "string", foreground="#444444"
        )  # Dunkelgrau für Strings
        self.tk_text.tag_configure(
            "comment", foreground="#444444", font=("Courier New", 16, "italic")
        )  # Dunkelgrau für Kommentare, aber kursiv
        self.tk_text.tag_configure(
            "operator", foreground="#444444"
        )  # Dunkelgrau für die meisten Operatoren
        self.tk_text.tag_configure("name", foreground="#444444")  # Dunkelgrau für Namen
        self.tk_text.tag_configure(
            "arrow", foreground="#444444"
        )  # Dunkelgrau für Pfeile
        self.tk_text.tag_configure(
            "bracket", foreground="#0000FF"
        )  # Starkes Blau für Klammern
        self.tk_text.tag_configure(
            "condition", foreground="#0000FF"
        )  # Blau für Bedingungen innerhalb von Klammern
        self.tk_text.tag_configure(
            "activity_content", foreground="#444444"
        )  # Dunkelgrau für Text in Aktivitäten

        # Prioritäten festlegen: Je niedriger die Zahl, desto höher die Priorität
        self.tk_text.tag_raise("comment")  # Höchste Priorität für Kommentare
        self.tk_text.tag_raise(
            "activity_content", "keyword"
        )  # Aktivitätstext hat Vorrang vor Schlüsselwörtern
        self.tk_text.tag_raise(
            "activity_content", "bracket"
        )  # Aktivitätstext hat Vorrang vor Klammern
        self.tk_text.tag_raise(
            "activity_content", "condition"
        )  # Aktivitätstext hat Vorrang vor Bedingungen
        self.tk_text.tag_raise(
            "activity_content", "arrow"
        )  # Aktivitätstext hat Vorrang vor Pfeilen

        # Initiales Update
        self.text_widget.bind(
            "<KeyRelease>", lambda event: self.update_text_and_button_state()
        )

        # Row 4: Footer with copyright notice
        self.footer = ctk.CTkFrame(self.root, fg_color="transparent", height=30)
        self.footer.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.footer.grid_propagate(False)  # Prevent frame from shrinking
        self.footer.columnconfigure(0, weight=1)
        self.copyright_label = ctk.CTkLabel(
            self.footer,
            text=f"© 2025 doubleSlash.de - PlantUML to Draw.io Converter v{VERSION} ({VERSION_DATE})",
            anchor="w",
            font=("Arial", 12),
        )
        self.copyright_label.grid(row=0, column=0, sticky="w")

        # Variable to store the current filename (without extension)
        self.current_file = None

    def create_menubar(self):
        """Erstellt eine Menüleiste für den schnellen Zugriff auf Hauptfunktionen."""
        import tkinter as tk

        menubar = tk.Menu(self.root)

        # "File" menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Datei öffnen", command=self.open_file, accelerator="Strg+O"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Beenden", command=self.root.quit, accelerator="Alt+F4"
        )
        menubar.add_cascade(label="Datei", menu=file_menu)

        # "Help" menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Über", command=self.show_about, accelerator="F1")
        menubar.add_cascade(label="Hilfe", menu=help_menu)

        self.root.config(menu=menubar)

        # Bind keyboard shortcuts
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<F1>", lambda event: self.show_about())
        self.root.bind("<Control-s>", lambda event: self.convert_to_drawio())

    def show_about(self):
        """Zeigt einen Informationsdialog über die Anwendung an."""
        from tkinter import messagebox

        messagebox.showinfo(
            "Über",
            f"PlantUML zu Draw.io Konverter\nVersion {VERSION}\n© 2025 doubleSlash.de",
        )

    def open_file(self):
        """Open a file and display it in the text widget."""
        file_types = [("PlantUML Files", "*.puml"), ("All Files", "*.*")]
        file_path = self.ctk.filedialog.askopenfilename(
            title="Select a PlantUML File", filetypes=file_types
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                self.text_widget.delete("1.0", self.ctk.END)
                self.text_widget.insert("1.0", content)
                self.current_file_path = file_path

                # Enable the convert button
                self.convert_button.configure(state="normal")

                # Update diagram type
                self.update_diagram_type(content)

                # Aktualisiere die Nachricht
                self.message_label.configure(text="PlantUML-Datei erfolgreich geladen.")
            except Exception as e:
                self.current_file_path = None
                self.filename_label.configure(
                    text="Keine Datei ausgewählt | Diagramm-Typ: -"
                )

                # Zeige Fehler in message_label statt im Text-Widget
                self.message_label.configure(text=f"Fehler beim Laden der Datei: {e}")

                # Disable convert button
                self.convert_button.configure(state="disabled")
        else:
            # Zeige Nachricht im message_label statt im Text-Widget
            self.message_label.configure(
                text="Bitte wählen Sie eine PlantUML-Datei zur Konvertierung aus."
            )

    def update_diagram_type(self, content):
        """Update the filename label to include diagram type info."""
        filename_text = (
            f"Geladene Datei: {os.path.basename(self.current_file_path)}"
            if hasattr(self, "current_file_path") and self.current_file_path
            else "Keine Datei ausgewählt"
        )

        if is_valid_activity_diagram(content):
            self.filename_label.configure(
                text=f"{filename_text} | Diagramm-Typ: Aktivitätsdiagramm"
            )
        else:
            self.filename_label.configure(
                text=f"{filename_text} | Diagramm-Typ: Unbekannt"
            )

    def update_text_and_button_state(self):
        """Update text widget state and enable/disable convert button based on content."""
        content = self.text_widget.get("1.0", "end")

        # Enable convert button only if valid PlantUML activity diagram detected
        if "@startuml" in content and "@enduml" in content:
            self.convert_button.configure(state="normal")
            # Update diagram type
            self.update_diagram_type(content)
        else:
            self.convert_button.configure(state="disabled")
            filename_text = (
                f"Geladene Datei: {os.path.basename(self.current_file_path)}"
                if hasattr(self, "current_file_path") and self.current_file_path
                else "Keine Datei ausgewählt"
            )
            self.filename_label.configure(text=f"{filename_text} | Diagramm-Typ: -")

    def apply_syntax_highlighting(self):
        """Wendet Syntax-Highlighting auf den PlantUML-Code im Textfeld an."""
        # 1. Entferne zunächst alle bestehenden Tags
        for tag in [
            "keyword",
            "string",
            "comment",
            "operator",
            "name",
            "arrow",
            "bracket",
            "condition",
            "activity_content",
        ]:
            self.tk_text.tag_remove(tag, "1.0", "end")

        # 2. Setze die Standardfarbe für den gesamten Text auf Dunkelgrau
        self.tk_text.configure(foreground="#444444")  # Dunkelgrau als Standardfarbe

        # Wende die verschiedenen Highlighting-Regeln an
        self._highlight_comments()
        self._highlight_activities()
        self._highlight_keywords()
        self._highlight_conditions()
        self._highlight_arrows()

    def _highlight_comments(self):
        """Markiert Kommentare im Code"""
        start_idx = "1.0"
        while True:
            pos = self.tk_text.search("'", start_idx, "end", regexp=False)
            if not pos:
                break

            # Markiere den Rest der Zeile als Kommentar
            lineend = self.tk_text.index(f"{pos} lineend")
            self.tk_text.tag_add("comment", pos, lineend)

            # Setze Startindex für nächste Suche
            start_idx = f"{lineend}+1c"

    def _highlight_activities(self):
        """Markiert Aktivitäten (Text in eckigen Klammern und zwischen : und ;)"""
        debug_mode = False  # Nur für Entwicklungszwecke auf True setzen

        # 1. Text in eckigen Klammern markieren
        start_idx = "1.0"
        while True:
            open_pos = self.tk_text.search("[", start_idx, "end", regexp=False)
            if not open_pos:
                break

            close_pos = self.tk_text.search("]", f"{open_pos}+1c", "end", regexp=False)
            if not close_pos:
                break

            # Markiere die Klammern selbst
            self.tk_text.tag_add("bracket", open_pos, f"{open_pos}+1c")
            self.tk_text.tag_add("bracket", close_pos, f"{close_pos}+1c")

            # Markiere den Inhalt als activity_content
            content_start = f"{open_pos}+1c"
            self.tk_text.tag_add("activity_content", content_start, close_pos)

            if debug_mode:
                activity_content = self.tk_text.get(content_start, close_pos)
                print(f"Aktivität in []: '{activity_content}'")

            # Setze Startindex für nächste Suche
            start_idx = f"{close_pos}+1c"

        # 2. Text zwischen : und ; markieren (alternative Aktivitätssyntax)
        start_idx = "1.0"
        while True:
            open_pos = self.tk_text.search(":", start_idx, "end", regexp=False)
            if not open_pos:
                break

            close_pos = self.tk_text.search(";", f"{open_pos}+1c", "end", regexp=False)
            if not close_pos:
                break

            # Markiere die Begrenzungszeichen selbst
            self.tk_text.tag_add("bracket", open_pos, f"{open_pos}+1c")
            self.tk_text.tag_add("bracket", close_pos, f"{close_pos}+1c")

            # Markiere den Inhalt zwischen : und ; als activity_content
            content_start = f"{open_pos}+1c"
            self.tk_text.tag_add("activity_content", content_start, close_pos)

            if debug_mode:
                activity_content = self.tk_text.get(content_start, close_pos)
                print(f"Aktivität zwischen : und ;: '{activity_content}'")

            # Setze Startindex für nächste Suche
            start_idx = f"{close_pos}+1c"

    def _highlight_keywords(self):
        """Markiert PlantUML-Schlüsselwörter"""
        keywords = [
            "@startuml",
            "@enduml",
            "start",
            "stop",
            "if",
            "then",
            "else",
            "endif",
            "while",
            "repeat",
            "fork",
            "end fork",
            "partition",
            "end partition",
            "backward",
            "forward",
            "detach",
            "note",
            "end note",
            "split",
            "end split",
        ]

        for keyword in keywords:
            start_idx = "1.0"
            while True:
                # Suche case-insensitive
                pos = self.tk_text.search(keyword, start_idx, "end", nocase=True)
                if not pos:
                    break

                end_pos = f"{pos}+{len(keyword)}c"

                # Prüfe ob diese Position bereits als activity_content markiert ist
                tags_here = self.tk_text.tag_names(pos)
                if "activity_content" not in tags_here:
                    self.tk_text.tag_add("keyword", pos, end_pos)

                # Setze Startindex für nächste Suche
                start_idx = end_pos

    def _highlight_conditions(self):
        """Markiert Bedingungen (Text in runden Klammern)"""
        start_idx = "1.0"
        while True:
            open_pos = self.tk_text.search("(", start_idx, "end", regexp=False)
            if not open_pos:
                break

            close_pos = self.tk_text.search(")", f"{open_pos}+1c", "end", regexp=False)
            if not close_pos:
                break

            # Prüfe ob innerhalb einer Aktivität
            tags_open = self.tk_text.tag_names(open_pos)
            if "activity_content" not in tags_open:
                # Markiere die Klammern
                self.tk_text.tag_add("bracket", open_pos, f"{open_pos}+1c")
                self.tk_text.tag_add("bracket", close_pos, f"{close_pos}+1c")

                # Markiere den Inhalt
                content_start = f"{open_pos}+1c"
                self.tk_text.tag_add("condition", content_start, close_pos)

            # Setze Startindex für nächste Suche
            start_idx = f"{close_pos}+1c"

    def _highlight_arrows(self):
        """Markiert Pfeile im PlantUML-Code"""
        arrow_patterns = ["->", "-->", "->>", "<-", "<--", "<<-", "..>", "<.."]
        for pattern in arrow_patterns:
            start_idx = "1.0"
            while True:
                pos = self.tk_text.search(pattern, start_idx, "end", regexp=False)
                if not pos:
                    break

                end_pos = f"{pos}+{len(pattern)}c"

                # Prüfe ob innerhalb einer Aktivität
                tags_here = self.tk_text.tag_names(pos)
                if "activity_content" not in tags_here:
                    self.tk_text.tag_add("arrow", pos, end_pos)

                # Setze Startindex für nächste Suche
                start_idx = end_pos

    def convert_to_drawio(self):
        """Convert the PlantUML diagram to Draw.io format."""
        if not self.current_file_path:
            # Zeige Nachricht im message_label statt im Text-Widget
            self.message_label.configure(
                text="Kein PlantUML-Code für die Konvertierung verfügbar."
            )
            return

        try:
            # Get content from text widget (in case user modified it)
            puml_content = self.text_widget.get("1.0", self.ctk.END)

            # Parse PlantUML
            try:
                # Process the diagram
                from plantuml2drawio.processors import ProcessorRegistry

                diagram_type, processor_class = ProcessorRegistry.detect_diagram_type(
                    puml_content
                )

                if not processor_class:
                    # Zeige Nachricht im message_label statt im Text-Widget
                    self.message_label.configure(
                        text=f"Fehler: Nicht unterstützter Diagrammtyp: {diagram_type}"
                    )
                    return

                processor = processor_class()

            except Exception as parse_error:
                # Zeige Nachricht im message_label statt im Text-Widget
                self.message_label.configure(
                    text=f"Fehler beim Parsen des PlantUML-Codes: {parse_error}"
                )
                return

            # Do layout
            try:
                # Anpassung der Methodenaufrufe an die tatsächliche API des Processors
                nodes, edges = processor.parse_diagram(puml_content)
                processor.layout_diagram(nodes, edges)
            except Exception as layout_error:
                # Zeige Nachricht im message_label statt im Text-Widget
                self.message_label.configure(
                    text=f"Fehler beim Layout des Diagramms: {layout_error}"
                )
                return

            # Generate XML
            try:
                xml_content = processor.convert_to_drawio(puml_content)
            except Exception as xml_error:
                # Zeige Nachricht im message_label statt im Text-Widget
                self.message_label.configure(
                    text=f"Fehler bei der XML-Generierung: {xml_error}"
                )
                return

            # Save dialog
            save_path = self._get_save_path()

            if save_path:
                try:
                    with open(save_path, "w", encoding="utf-8") as file:
                        file.write(xml_content)
                    # Zeige Nachricht im message_label statt im Text-Widget
                    self.message_label.configure(
                        text=f"Draw.io-Datei erstellt: {save_path}"
                    )
                except Exception as io_error:
                    # Zeige Nachricht im message_label statt im Text-Widget
                    self.message_label.configure(
                        text=f"Fehler beim Speichern der Datei: {io_error}"
                    )
            else:
                # Zeige Nachricht im message_label statt im Text-Widget
                self.message_label.configure(text="Speichern abgebrochen.")

        except Exception as e:
            # Zeige Nachricht im message_label statt im Text-Widget
            self.message_label.configure(text=f"Fehler während der Konvertierung: {e}")

    def _get_save_path(self):
        """Show a save dialog and return the selected path or None if cancelled."""
        # Determine default filename
        default_filename = (
            f"{os.path.splitext(os.path.basename(self.current_file_path))[0]}.drawio"
            if self.current_file_path
            else "untitled.drawio"
        )

        # Show save dialog to choose storage location
        save_path = self.ctk.filedialog.asksaveasfilename(
            title="Draw.io-Datei speichern",
            initialfile=default_filename,
            defaultextension=".drawio",
            filetypes=[("Draw.io Files", "*.drawio")],
        )

        return save_path


def main():
    # Import erst bei Bedarf, um die Startzeit zu verkürzen
    import customtkinter as ctk

    # Splash-Screen Optionen (können implementiert werden, um die wahrgenommene Startzeit zu verringern)
    # splash_visible = False
    # try:
    #    # Hier könnte ein minimaler Splash-Screen gezeigt werden
    #    # splash_visible = True
    # except:
    #    pass

    root = ctk.CTk()
    # Set application title in the menu bar
    root.title("plantuml2drawio")

    # Icon-Handling verzögern - wir benutzen ein Fallback ohne Exception
    if sys.platform.startswith("win"):
        try:
            root.after(100, lambda: root.iconbitmap("p2dapp_icon.ico"))
        except:
            pass
    else:

        def set_icon():
            try:
                import tkinter as tk

                icon = tk.PhotoImage(file="p2dapp_icon.png")
                root.iconphoto(False, icon)
            except:
                pass

        root.after(100, set_icon)

    app = FileSelectorApp(root)

    # Fenster erst nach vollständigem Laden in den Vordergrund bringen
    def bring_to_front():
        root.lift()
        root.attributes("-topmost", True)
        root.after(100, lambda: root.focus_force())
        root.after(500, lambda: root.attributes("-topmost", False))

    root.after(200, bring_to_front)

    root.mainloop()


if __name__ == "__main__":
    main()
