#!/usr/bin/env python3
import os
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from p2dcore import parse_plantuml_activity, create_drawio_xml, is_valid_plantuml_activitydiagram, layout_activitydiagram

# Versionsnummer als Konstante
VERSION = "1.0.8"

class FileSelectorApp:
    def __init__(self, root):
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
        self.root.rowconfigure(3, weight=1)  # Row 3 (main frame) is now dynamically expandable

        # Row 0: Filename label
        self.filename_label = ctk.CTkLabel(
            self.root, 
            text="Keine Datei ausgewählt.",
            anchor="w",
            font=("Arial", 14)
        )
        self.filename_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Row 1: Horizontal button frame
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        # "Open File" button on the left
        self.file_button = ctk.CTkButton(
            self.button_frame, 
            text="Datei öffnen", 
            command=self.open_file,
            font=("Arial", 14, "bold"),
            width=120,
            height=40,
            corner_radius=50,
            fg_color="#00759e"
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
            fg_color="#00759e"
        )
        self.convert_button.grid(row=0, column=2, sticky="e")

        # Row 2: Message label
        self.message_label = ctk.CTkLabel(
            self.root, 
            text="Bitte wählen Sie eine PlantUML-Datei zur Konvertierung aus.",
            anchor="w",
            font=("Arial", 14)
        )
        self.message_label.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Row 3: Main frame for the text widget
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Text widget to display file contents
        self.text_widget = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=("Courier New", 16)
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        
        # Farbdefinitionen für das Syntax-Highlighting
        # Zugriff auf das zugrundeliegende Tkinter-Text-Widget
        self.tk_text = self.text_widget._textbox
        # Setze alle Farben zunächst auf Dunkelgrau (statt Schwarz) für den normalen Text
        self.tk_text.configure(foreground="#444444")  # Dunkelgrau als Standardfarbe
        self.tk_text.tag_configure("keyword", foreground="#FF00FF")  # Magenta für Schlüsselwörter
        self.tk_text.tag_configure("string", foreground="#444444")   # Dunkelgrau für Strings
        self.tk_text.tag_configure("comment", foreground="#444444", font=("Courier New", 16, "italic"))  # Dunkelgrau für Kommentare, aber kursiv
        self.tk_text.tag_configure("operator", foreground="#444444") # Dunkelgrau für die meisten Operatoren
        self.tk_text.tag_configure("name", foreground="#444444")     # Dunkelgrau für Namen
        self.tk_text.tag_configure("arrow", foreground="#444444")    # Dunkelgrau für Pfeile
        self.tk_text.tag_configure("bracket", foreground="#0000FF")  # Starkes Blau für Klammern
        self.tk_text.tag_configure("condition", foreground="#0000FF")  # Blau für Bedingungen innerhalb von Klammern
        self.tk_text.tag_configure("activity_content", foreground="#444444")  # Dunkelgrau für Text in Aktivitäten
        
        # Prioritäten festlegen: Je niedriger die Zahl, desto höher die Priorität
        self.tk_text.tag_raise("comment")        # Höchste Priorität für Kommentare
        self.tk_text.tag_raise("activity_content", "keyword")  # Aktivitätstext hat Vorrang vor Schlüsselwörtern
        self.tk_text.tag_raise("activity_content", "bracket")  # Aktivitätstext hat Vorrang vor Klammern
        self.tk_text.tag_raise("activity_content", "condition")  # Aktivitätstext hat Vorrang vor Bedingungen
        self.tk_text.tag_raise("activity_content", "arrow")  # Aktivitätstext hat Vorrang vor Pfeilen
        
        # Initiales Update
        self.text_widget.bind("<KeyRelease>", lambda event: self.update_text_and_button_state())
        
        # Row 4: Footer with copyright notice
        self.footer = ctk.CTkFrame(self.root, fg_color="transparent")
        self.footer.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.footer.columnconfigure(0, weight=1)
        self.copyright_label = ctk.CTkLabel(
            self.footer,
            text=f"© 2025 doubleSlash.de - Version {VERSION}",
            anchor="w",
            font=("Arial", 12)
        )
        self.copyright_label.grid(row=0, column=0, sticky="w")
        
        # Variable to store the current filename (without extension)
        self.current_file = None
    
    def create_menubar(self):
        """Erstellt eine Menüleiste für den schnellen Zugriff auf Hauptfunktionen."""
        menubar = tk.Menu(self.root)
        
        # "File" menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Datei öffnen", command=self.open_file, accelerator="Strg+O")
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit, accelerator="Alt+F4")
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
        messagebox.showinfo("Über", f"PlantUML zu Draw.io Konverter\nVersion {VERSION}\n© 2025 doubleSlash.de")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Datei auswählen",
            filetypes=[("PlantUML und Text Dateien", ("*.puml", "*.txt", "*.plantuml", "*.uml"))]
        )
        if file_path:
            self.current_file = os.path.splitext(os.path.basename(file_path))[0]
            self.filename_label.configure(text=f"Geladene Datei: {os.path.basename(file_path)}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                # Display file content in the text widget
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("end", content)
                # Syntax-Highlighting anwenden
                self.apply_syntax_highlighting()
                # Update button state
                self.update_text_and_button_state()
            except Exception as e:
                self.message_label.configure(text=f"Fehler beim Laden der Datei: {e}")
                self.convert_button.configure(state="disabled")
        else:
            self.filename_label.configure(text="Keine Datei ausgewählt.")
            self.message_label.configure(text="Bitte wählen Sie eine PlantUML-Datei zur Konvertierung aus.")
            # Reset text widget
            self.text_widget.delete("1.0", "end")
            self.convert_button.configure(state="disabled")

    def update_text_and_button_state(self):
        """Aktualisiert den Button-Status basierend auf dem aktuellen Textinhalt."""
        content = self.text_widget.get("1.0", "end")
        is_valid = is_valid_plantuml_activitydiagram(content)
        
        # Apply syntax highlighting
        self.apply_syntax_highlighting()
        
        # Update Convert button state
        if is_valid:
            self.convert_button.configure(state="normal")
            self.message_label.configure(text="Gültiges PlantUML-Aktivitätsdiagramm.")
        else:
            self.convert_button.configure(state="disabled")
            self.message_label.configure(text="Ungültiges PlantUML-Aktivitätsdiagramm. Konvertierung deaktiviert.")

    def apply_syntax_highlighting(self):
        """Wendet Syntax-Highlighting auf den PlantUML-Code im Textfeld an."""
        # 1. Entferne zunächst alle bestehenden Tags
        for tag in ["keyword", "string", "comment", "operator", "name", "arrow", "bracket", "condition", "activity_content"]:
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
            "@startuml", "@enduml", "start", "stop", "if", "then", "else", "endif",
            "while", "repeat", "fork", "end fork", "partition", "end partition", 
            "backward", "forward", "detach", "note", "end note", "split", "end split"
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
        arrow_patterns = ["->", "-->", "->>", "<-", "<--", "<<-", "..>", "<.." ]
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
        # Hole den Inhalt des Text-Widgets (PlantUML-Code)
        plantuml_code = self.text_widget.get("1.0", "end")
        if not plantuml_code.strip():
            self.message_label.configure(text="Kein PlantUML-Code für die Konvertierung verfügbar.")
            return

        try:
            # Parse PlantUML code into nodes and edges
            try:
                nodes, edges = parse_plantuml_activity(plantuml_code)
            except Exception as parse_error:
                self.message_label.configure(text=f"Fehler beim Parsen des PlantUML-Codes: {parse_error}")
                return
                
            # Optimize diagram layout
            try:
                drawio_xml = layout_activitydiagram(nodes, edges)
            except Exception as layout_error:
                self.message_label.configure(text=f"Fehler beim Layout des Diagramms: {layout_error}")
                return
                
            # Generate XML for draw.io
            try:
                drawio_xml = create_drawio_xml(nodes, edges)
            except Exception as xml_error:
                self.message_label.configure(text=f"Fehler bei der XML-Generierung: {xml_error}")
                return

            # Determine default filename
            default_filename = f"{self.current_file}.drawio" if self.current_file else "untitled.drawio"

            # Show save dialog to choose storage location
            save_path = filedialog.asksaveasfilename(
                title="Draw.io-Datei speichern",
                initialfile=default_filename,
                defaultextension=".drawio",
                filetypes=[("Draw.io Files", "*.drawio")]
            )

            if save_path:
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(drawio_xml)
                    self.message_label.configure(text=f"Draw.io-Datei erstellt: {save_path}")
                except IOError as io_error:
                    self.message_label.configure(text=f"Fehler beim Speichern der Datei: {io_error}")
            else:
                self.message_label.configure(text="Speichern abgebrochen.")
        except Exception as e:
            import traceback
            print(f"Unerwarteter Fehler während der Konvertierung: {e}")
            print(traceback.format_exc())
            self.message_label.configure(text=f"Fehler während der Konvertierung: {e}")

def main():
    root = ctk.CTk()
    # Set application title in the menu bar
    root.title("plantuml2drawio")
    
    # Icon-Handhabung mit verbesserter Fehlerbehandlung
    import sys
    import os
    
    def set_app_icon():
        """Setzt das Anwendungsicon basierend auf dem Betriebssystem"""
        icon_path = None
        
        # Pfade zu möglichen Icon-Dateien
        icon_locations = [
            # Aktuelle Arbeitsverzeichnis
            os.path.join(os.getcwd(), "p2dapp_icon.ico"),
            os.path.join(os.getcwd(), "p2dapp_icon.png"),
            # Verzeichnis der Skriptdatei
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2dapp_icon.ico"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2dapp_icon.png"),
        ]
        
        # Finde die erste existierende Icon-Datei
        for path in icon_locations:
            if os.path.exists(path):
                icon_path = path
                break
        
        if not icon_path:
            print("Warnung: Keine Icon-Datei gefunden.")
            return False
            
        try:
            if sys.platform.startswith('win') and icon_path.endswith('.ico'):
                root.iconbitmap(icon_path)
                return True
            elif icon_path.endswith('.png'):
                import tkinter as tk
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(False, icon)
                return True
        except Exception as e:
            print(f"Fehler beim Setzen des Icons: {e}")
        
        return False
    
    # Versuche, das Icon zu setzen
    set_app_icon()

    app = FileSelectorApp(root)
    
    # Bring window to the front
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 