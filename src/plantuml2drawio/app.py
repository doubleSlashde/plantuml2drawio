"""GUI application for converting PlantUML diagrams to Draw.io format."""

import os
import sys
from pathlib import Path
from tkinter import filedialog

from plantuml2drawio.processors.activity_processor import (
    create_activity_drawio_xml, layout_activity_diagram,
    parse_activity_diagram)

# Version number as constant
VERSION = "1.2.0"

from plantuml2drawio.processors import is_valid_activity_diagram
# Importiere die Funktion aus dem neuen Modul mit dem neuen Namen
from plantuml2drawio.processors.activity_processor import (
    is_valid_activity_diagram, layout_activity_diagram, parse_activity_diagram)


class FileSelectorApp:
    """Main application window for the PlantUML to Draw.io converter.

    This class handles the GUI interface for selecting, viewing, and converting
    PlantUML files to Draw.io format.
    """

    def __init__(self, root):
        """Initialize the application window.

        Args:
            root: The root window of the application.
        """
        # Delayed import of customtkinter inside the class
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
        self.root.rowconfigure(
            3, weight=1
        )  # Only the main frame (text widget) should expand

        # Row 0: Filename label
        self.filename_label = ctk.CTkLabel(
            self.root, text="Keine Datei ausgewählt.", anchor="w", font=("Arial", 14)
        )
        self.filename_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        # Row 1: Diagram type label
        self.diagram_type_label = ctk.CTkLabel(
            self.root, text="Diagramm-Typ: -", anchor="w", font=("Arial", 14)
        )
        self.diagram_type_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Row 1.5: Message label for errors and status updates
        self.message_label = ctk.CTkLabel(
            self.root,
            text="",
            anchor="w",
            font=("Arial", 14),
            text_color="red",  # Error messages will be shown in red
        )
        self.message_label.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 5))

        # Row 2: Horizontal button frame
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=50)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))
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

        # Row 3: Main frame for the text widget (moved from row 4)
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
            text=f"© 2025 doubleSlash.de - Version {VERSION}",
            anchor="w",
            font=("Arial", 12),
        )
        self.copyright_label.grid(row=0, column=0, sticky="w")

        # Variable to store the current filename (without extension)
        self.current_file = None

    def create_menubar(self):
        """Create the application menu bar with File and Help menus."""
        menubar = self.ctk.CTkFrame(self.root)
        menubar.pack(fill="x")

        # File menu
        file_menu = self.ctk.CTkFrame(menubar)
        file_menu.pack(side="left", padx=5)

        open_button = self.ctk.CTkButton(
            file_menu, text="Open", command=self.open_file, width=80
        )
        open_button.pack(side="left", padx=2)

        # Help menu
        help_menu = self.ctk.CTkFrame(menubar)
        help_menu.pack(side="right", padx=5)

        about_button = self.ctk.CTkButton(
            help_menu, text="About", command=self.show_about, width=80
        )
        about_button.pack(side="right", padx=2)

    def show_about(self):
        """Display the about dialog with version information."""
        about_text = (
            f"PlantUML to Draw.io Converter\n"
            f"Version: {VERSION}\n\n"
            "Created by doubleSlash.de"
        )
        self.show_info("About", about_text)

    def show_error(self, message: str):
        """Display an error message dialog.

        Args:
            message: The error message to display.
        """
        self.ctk.CTkMessagebox(title="Error", message=message, icon="cancel")

    def show_success(self, message: str):
        """Display a success message dialog.

        Args:
            message: The success message to display.
        """
        self.ctk.CTkMessagebox(title="Success", message=message, icon="check")

    def show_info(self, title: str, message: str):
        """Display an information dialog.

        Args:
            title: The dialog title.
            message: The information message to display.
        """
        self.ctk.CTkMessagebox(title=title, message=message, icon="info")

    def open_file(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Datei auswählen",
            filetypes=[
                (
                    "PlantUML und Text Dateien",
                    ("*.puml", "*.txt", "*.plantuml", "*.uml"),
                )
            ],
        )
        if file_path:
            self.current_file = os.path.splitext(os.path.basename(file_path))[0]
            self.filename_label.configure(
                text=f"Geladene Datei: {os.path.basename(file_path)}"
            )
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                # Display file content in the text widget
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("end", content)
                # Reset diagram type label before checking new content
                self.diagram_type_label.configure(text="Diagramm-Typ: -")
                # Syntax-Highlighting anwenden
                self.apply_syntax_highlighting()
                # Update button state and diagram type
                self.update_text_and_button_state()
            except Exception as e:
                self.diagram_type_label.configure(
                    text=f"Fehler beim Laden der Datei: {e}"
                )
                self.convert_button.configure(state="disabled")
        # Wenn der Dialog abgebrochen wurde (file_path ist leer),
        # dann machen wir nichts und behalten den aktuellen Zustand bei

    def update_text_and_button_state(self):
        """Aktualisiert den Button-Status basierend auf dem aktuellen Textinhalt."""
        content = self.text_widget.get("1.0", "end")
        is_valid = is_valid_activity_diagram(content)

        # Update diagram type label
        if is_valid:
            self.diagram_type_label.configure(text="Diagramm-Typ: Aktivitätsdiagramm")
            self.convert_button.configure(state="normal")
        else:
            self.diagram_type_label.configure(text="Diagramm-Typ: Unbekannt")
            self.convert_button.configure(state="disabled")

        # Apply syntax highlighting
        self.apply_syntax_highlighting()

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
        """Convert the current PlantUML diagram to Draw.io format.

        This method handles the conversion process and saves the result
        to a new file with the appropriate extension.
        """
        try:
            input_file = self.text_widget.get("1.0", "end")
            if not input_file.strip():
                self.message_label.configure(
                    text="Kein PlantUML-Code für die Konvertierung verfügbar."
                )
                return

            # Parse PlantUML code into nodes and edges
            try:
                diagram_data = parse_activity_diagram(input_file)
                nodes = [
                    Node(
                        id=node["id"],
                        label=node["label"],
                        shape=node["shape"],
                        x=node["x"],
                        y=node["y"],
                        width=node["width"],
                        height=node["height"],
                    )
                    for node in diagram_data["nodes"]
                ]
                edges = [
                    Edge(
                        id=edge["id"],
                        source=edge["source"],
                        target=edge["target"],
                        label=edge["label"],
                    )
                    for edge in diagram_data["edges"]
                ]
            except Exception as parse_error:
                self.message_label.configure(
                    text=f"Fehler beim Parsen des PlantUML-Codes: {parse_error}"
                )
                return

            # Optimize diagram layout
            try:
                layout_activity_diagram(nodes, edges)
            except Exception as layout_error:
                self.message_label.configure(
                    text=f"Fehler beim Layout des Diagramms: {layout_error}"
                )
                return

            # Generate XML for draw.io
            try:
                drawio_xml = create_activity_drawio_xml(nodes, edges)
            except Exception as xml_error:
                self.message_label.configure(
                    text=f"Fehler bei der XML-Generierung: {xml_error}"
                )
                return

            # Determine default filename
            default_filename = (
                f"{self.current_file}.drawio"
                if self.current_file
                else "untitled.drawio"
            )

            # Show save dialog to choose storage location
            save_path = filedialog.asksaveasfilename(
                title="Draw.io-Datei speichern",
                initialfile=default_filename,
                defaultextension=".drawio",
                filetypes=[("Draw.io Files", "*.drawio")],
            )

            if save_path:
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(drawio_xml)
                    self.message_label.configure(
                        text=f"Draw.io-Datei erstellt: {save_path}"
                    )
                except IOError as io_error:
                    self.message_label.configure(
                        text=f"Fehler beim Speichern der Datei: {io_error}"
                    )
            else:
                self.message_label.configure(text="Speichern abgebrochen.")
        except Exception as e:
            import traceback

            print(f"Unerwarteter Fehler während der Konvertierung: {e}")
            print(traceback.format_exc())
            self.message_label.configure(text=f"Fehler während der Konvertierung: {e}")


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
    try:
        root.after(100, lambda: root.iconbitmap("p2dapp_icon.ico"))
    except FileNotFoundError:
        # Icon file not found, continue without icon
        pass
    except Exception as e:
        # Log other unexpected errors but continue
        print(f"Warning: Could not set window icon: {e}", file=sys.stderr)

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
