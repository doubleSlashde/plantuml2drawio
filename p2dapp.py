import os
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from p2dcore import parse_plantuml_activity, create_drawio_xml, is_valid_plantuml_activitydiagram_string, layout_activitydiagram
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

# Versionsnummer als Konstante
VERSION = "1.0.8"

class FileSelectorApp:
    def __init__(self, root):
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
        # Entferne bestehende Tags
        for tag in ["keyword", "string", "comment", "operator", "name", "arrow", "bracket"]:
            self.tk_text.tag_remove(tag, "1.0", "end")
        
        # Wichtige Schlüsselwörter, die in Magenta hervorgehoben werden sollen
        keywords = [
            # Basis-Keywords
            "@startuml", "@enduml", "start", "stop", "if", "then", "else", "endif",
            "while", "repeat", "fork", "end fork",
            # Erweiterte Keywords
            "partition", "end partition", "backward", "forward", "detach",
            "note", "end note", "split", "end split"
        ]

        # 1. Kommentare hervorheben (sie sollen Vorrang vor allem anderen haben)
        start_idx = "1.0"
        while True:
            pos = self.tk_text.search("'", start_idx, "end")
            if not pos:
                break
            line, col = map(int, pos.split('.'))
            
            # Suche das Ende der Zeile
            lineend = self.tk_text.index(f"{line+1}.0")
            if not lineend:
                lineend = "end"
            
            # Markiere die gesamte Zeile ab dem Kommentarzeichen
            self.tk_text.tag_add("comment", pos, lineend)
            start_idx = lineend
        
        # 2. Klammern hervorheben
        bracket_patterns = ["(", ")", "[", "]", "{", "}", "<", ">"]
        for pattern in bracket_patterns:
            start_idx = "1.0"
            while True:
                pos = self.tk_text.search(pattern, start_idx, "end")
                if not pos:
                    break
                end_pos = f"{pos}+1c"  # Ein Zeichen vorwärts
                self.tk_text.tag_add("bracket", pos, end_pos)
                start_idx = end_pos

        # 3. PlantUML-spezifische Pfeile hervorheben
        arrow_patterns = ["->", "-->", "->>", "-->", "..>", "<-", "<--", "<<-", "<--", "<.." ]
        for pattern in arrow_patterns:
            start_idx = "1.0"
            while True:
                pos = self.tk_text.search(pattern, start_idx, "end")
                if not pos:
                    break
                end_pos = f"{pos}+{len(pattern)}c"  # Länge des Musters vorwärts
                self.tk_text.tag_add("arrow", pos, end_pos)
                start_idx = end_pos
        
        # 4. Schlüsselwörter hervorheben - dabei Groß-/Kleinschreibung ignorieren
        # Für jedes Schlüsselwort in unserer Liste
        for keyword in keywords:
            start_idx = "1.0"
            while True:
                # Suche nach dem Schlüsselwort, ignoriere Groß-/Kleinschreibung
                pos = self.tk_text.search(keyword, start_idx, "end", nocase=True)
                if not pos:
                    break
                    
                # Berechne End-Position
                end_pos = f"{pos}+{len(keyword)}c"
                
                # Prüfe Wortgrenzen - das Zeichen vor und nach dem Schlüsselwort sollte kein Buchstabe/Zahl sein
                is_valid_keyword = True
                
                # Prüfe Zeichen vor dem Schlüsselwort, falls nicht am Anfang
                if self.tk_text.compare(pos, ">", "1.0"):
                    before_pos = f"{pos}-1c"
                    char_before = self.tk_text.get(before_pos, pos)
                    if char_before.isalnum() or char_before == '_':
                        is_valid_keyword = False
                
                # Prüfe Zeichen nach dem Schlüsselwort, falls nicht am Ende
                if is_valid_keyword and self.tk_text.compare(end_pos, "<", "end"):
                    char_after = self.tk_text.get(end_pos, f"{end_pos}+1c")
                    if char_after.isalnum() or char_after == '_':
                        is_valid_keyword = False
                
                # Wenn es ein gültiges Schlüsselwort ist, markiere es
                if is_valid_keyword:
                    # Hole den tatsächlichen Text, um die korrekte Groß-/Kleinschreibung beizubehalten
                    actual_text = self.tk_text.get(pos, end_pos)
                    self.tk_text.tag_add("keyword", pos, end_pos)
                
                # Setze Startindex für nächste Suche
                start_idx = end_pos

    def convert_to_drawio(self):
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
    root = ctk.CTk()
    # Set application title in the menu bar
    root.title("plantuml2drawio")
    
    import sys
    # Set icon in a cross-platform manner
    if sys.platform.startswith('win'):
        try:
            root.iconbitmap("p2dapp_icon.ico")
        except Exception as e:
            print("Error loading icon on Windows:", e)
    else:
        try:
            # Für CustomTkinter muss Iconhandling überprüft werden
            import tkinter as tk
            icon = tk.PhotoImage(file="p2dapp_icon.png")
            root.iconphoto(False, icon)
        except Exception as e:
            print("Error loading icon on macOS/Linux:", e)

    app = FileSelectorApp(root)
    
    # Bring window to the front
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 