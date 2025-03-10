#!/usr/bin/env python3
import os
import sys

# Versionsnummer als Konstante
VERSION = "1.0.8"

# Nur die essentiellen Funktionen aus p2dcore importieren
# Andere Importe werden verzögert, wenn sie benötigt werden
from p2dcore import is_valid_plantuml_activitydiagram_string

class FileSelectorApp:
    def __init__(self, root):
        # Verzögerter Import von customtkinter innerhalb der Klasse
        import customtkinter as ctk
        self.ctk = ctk
        
        self.root = root
        self.root.title("PlantUML to Draw.io Converter")
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
            text="No file selected.",
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
            text="Open File", 
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
            text="Convert to Draw.io", 
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
            text="Please select a PlantUML file to convert.",
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
        import tkinter as tk
        menubar = tk.Menu(self.root)
        
        # "File" menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # "Help" menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about, accelerator="F1")
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<F1>", lambda event: self.show_about())
        self.root.bind("<Control-s>", lambda event: self.convert_to_drawio())
    
    def show_about(self):
        """Zeigt einen Informationsdialog über die Anwendung an."""
        from tkinter import messagebox
        messagebox.showinfo("About", f"PlantUML to Draw.io Converter\nVersion {VERSION}\n© 2025 doubleSlash.de")

    def open_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("PlantUML and Text Files", ("*.puml", "*.txt", "*.plantuml", "*.uml"))]
        )
        if file_path:
            self.current_file = os.path.splitext(os.path.basename(file_path))[0]
            self.filename_label.configure(text=f"Loaded file: {os.path.basename(file_path)}")
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
                self.message_label.configure(text=f"Error loading file: {e}")
                self.convert_button.configure(state="disabled")
        else:
            self.filename_label.configure(text="No file selected.")
            self.message_label.configure(text="Please select a PlantUML file to convert.")
            # Reset text widget
            self.text_widget.delete("1.0", "end")
            self.convert_button.configure(state="disabled")

    def update_text_and_button_state(self):
        """Aktualisiert den Button-Status basierend auf dem aktuellen Textinhalt."""
        content = self.text_widget.get("1.0", "end")
        is_valid = is_valid_plantuml_activitydiagram_string(content)
        
        # Apply syntax highlighting
        self.apply_syntax_highlighting()
        
        # Update Convert button state
        if is_valid:
            self.convert_button.configure(state="normal")
            self.message_label.configure(text="Valid PlantUML activity diagram.")
        else:
            self.convert_button.configure(state="disabled")
            self.message_label.configure(text="Invalid PlantUML activity diagram. Conversion disabled.")

    def apply_syntax_highlighting(self):
        """Wendet Syntax-Highlighting auf den PlantUML-Code im Textfeld an."""
        # 1. Entferne zunächst alle bestehenden Tags
        for tag in ["keyword", "string", "comment", "operator", "name", "arrow", "bracket", "condition", "activity_content"]:
            self.tk_text.tag_remove(tag, "1.0", "end")
        
        # 2. Setze die Standardfarbe für den gesamten Text auf Dunkelgrau
        self.tk_text.configure(foreground="#444444")  # Dunkelgrau als Standardfarbe
        
        # EINFACHSTER ANSATZ:
        # 1. Schritt: Markiere alle Kommentare
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
        
        # 2. Schritt: Markiere alle Aktivitäten (Text in eckigen Klammern)
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
            
            # Setze Startindex für nächste Suche
            start_idx = f"{close_pos}+1c"
        
        # 3. Schritt: Markiere Schlüsselwörter, aber nur wenn sie nicht bereits als activity_content markiert sind
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
        
        # 4. Schritt: Markiere runde Klammern und ihren Inhalt
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
        
        # 5. Schritt: Markiere Pfeile
        arrow_patterns = ["->", "-->", "->>", "-->", "..>", "<-", "<--", "<<-", "<--", "<.." ]
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
        # Importiere die benötigten Module erst jetzt, da sie nur für die Konvertierung benötigt werden
        from p2dcore import parse_plantuml_activity, create_drawio_xml, layout_activitydiagram
        from tkinter import filedialog
        
        # Hole den Inhalt des Text-Widgets (PlantUML-Code)
        plantuml_code = self.text_widget.get("1.0", "end")
        if not plantuml_code.strip():
            self.message_label.configure(text="No PlantUML code available for conversion.")
            return

        try:
            # Parse PlantUML code into nodes and edges
            nodes, edges = parse_plantuml_activity(plantuml_code)
            # Optimize diagram layout
            drawio_xml = layout_activitydiagram(nodes, edges)
            # Generate XML for draw.io
            drawio_xml = create_drawio_xml(nodes, edges)

            # Determine default filename
            default_filename = f"{self.current_file}.drawio" if self.current_file else "untitled.drawio"

            # Show save dialog to choose storage location
            save_path = filedialog.asksaveasfilename(
                title="Save Draw.io File",
                initialfile=default_filename,
                defaultextension=".drawio",
                filetypes=[("Draw.io Files", "*.drawio")]
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(drawio_xml)
                self.message_label.configure(text=f"Draw.io file created: {save_path}")
            else:
                self.message_label.configure(text="Save cancelled.")
        except Exception as e:
            self.message_label.configure(text=f"Error during conversion: {e}")

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
    if sys.platform.startswith('win'):
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