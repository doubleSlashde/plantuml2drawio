import tkinter as tk
from tkinter import filedialog
import os
import tempfile
from p2dcore import parse_plantuml_activity, create_drawio_xml, is_valid_plantuml_activitydiagram_string
import tkinter.font as tkFont

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PlantUML to Draw.io Converter")
        self.root.geometry("800x600")  # Larger window for better overview

        # Create menubar
        self.create_menubar()

        # Configure main grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)  # Row 2 (main frame) is dynamically expandable

        # Row 0: Filename label
        self.filename_label = tk.Label(
            self.root, 
            text="No file selected.",
            anchor="w",
            font=("Arial", 12)
        )
        self.filename_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Row 1: Message label (for hints and error messages)
        self.message_label = tk.Label(
            self.root, 
            text="",
            anchor="w",
            font=("Arial", 12)
        )
        self.message_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Row 2: Main frame for the text widget and scrollbar (ensures responsive design)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Default font for the text widget
        self.default_font = tkFont.Font(family="Courier New", size=14)
        
        # Text widget to display file contents
        self.text_widget = tk.Text(
            self.main_frame, 
            wrap="word",
            font=self.default_font
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        self.text_widget.tag_configure("plantuml", foreground="#800000", font=self.default_font)
        self.text_widget.tag_configure("keyword", foreground="#F000F0", font=self.default_font)
        self.text_widget.tag_configure("condition", foreground="blue", font=self.default_font)
        
        # Bind syntax highlighting (changes here only affect highlighting; 
        # the button remains unaffected)
        self.text_widget.bind("<KeyRelease>", lambda event: self.highlight_plant_uml_activity())

        # Vertical scrollbar for the text widget
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.text_widget.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        # Row 3: Horizontal button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        # "Open File" button on the left
        self.file_button = tk.Button(self.button_frame, text="Open File", command=self.open_file)
        self.file_button.grid(row=0, column=0, sticky="w")

        # Spacer in the middle
        spacer = tk.Label(self.button_frame, text="")
        spacer.grid(row=0, column=1, sticky="ew")

        # "Convert to Draw.io" button on the right; 
        # initially disabled
        self.convert_button = tk.Button(
            self.button_frame, 
            text="Convert to Draw.io", 
            command=self.convert_to_drawio,
            state=tk.DISABLED
        )
        self.convert_button.grid(row=0, column=2, sticky="e")

        # Row 4: Footer with copyright notice
        self.footer = tk.Frame(self.root)
        self.footer.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.footer.columnconfigure(0, weight=1)
        self.copyright_label = tk.Label(
            self.footer,
            text="© 2025 doubleSlash.de",
            anchor="w",
            font=("Arial", 10)
        )
        self.copyright_label.grid(row=0, column=0, sticky="w")

        # Variable to store the current filename (without extension)
        self.current_file = None
    
    def create_menubar(self):
        """Creates a menu bar for quick access to main functions."""
        menubar = tk.Menu(self.root)
        
        # "File" menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # "Help" menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def show_about(self):
        """Displays an information dialog about the application."""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("About", "PlantUML to Draw.io Converter\n© 2025 doubleSlash.de")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("PlantUML and Text Files", ("*.puml", "*.txt", "*.plantuml", "*.uml"))]
        )
        if file_path:
            self.current_file = os.path.splitext(os.path.basename(file_path))[0]
            self.filename_label.config(text=f"Loaded File: {os.path.basename(file_path)}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                if not is_valid_plantuml_activitydiagram_string(content):
                    self.message_label.config(text="Invalid PlantUML activity diagram. Conversion disabled.")
                    self.convert_button.config(state=tk.DISABLED)
                else:
                    self.message_label.config(text="File loaded successfully.")
                    self.convert_button.config(state=tk.NORMAL)
            except Exception as e:
                content = ""
                self.message_label.config(text=f"Error loading file: {e}")
                self.convert_button.config(state=tk.DISABLED)
        else:
            self.filename_label.config(text="No file selected.")
            self.message_label.config(text="No file selected.")
            content = ""
            self.convert_button.config(state=tk.DISABLED)
        
        # Display file content in the text widget
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, content)
        # Execute syntax highlighting (without affecting the button state)
        self.highlight_plant_uml_activity()

    def highlight_plant_uml_activity(self):
        """Executes syntax highlighting **only** if a valid PlantUML activity diagram is present."""
        content = self.text_widget.get("1.0", tk.END)
        if not is_valid_plantuml_activitydiagram_string(content):
            # If the content is not valid, existing tags are removed.
            self.text_widget.tag_remove("keyword", "1.0", tk.END)
            self.text_widget.tag_remove("condition", "1.0", tk.END)
            return

        # Remove existing tags first
        self.text_widget.tag_remove("keyword", "1.0", tk.END)
        self.text_widget.tag_remove("condition", "1.0", tk.END)
        
        # Highlight keywords
        for pattern in ["if", "then", "else", "endif", "start", "stop", "@startuml", "@enduml"]:
            start_idx = "1.0"
            while True:
                pos = self.text_widget.search(pattern, start_idx, stopindex=tk.END)
                if not pos:
                    break
                end_pos = f"{pos}+{len(pattern)}c"
                self.text_widget.tag_add("keyword", pos, end_pos)
                start_idx = end_pos
        
        # Highlight conditions that are in parentheses directly following "if"
        start_search = 0
        while True:
            if_idx = content.find("if", start_search)
            if if_idx == -1:
                break
            
            open_paren_idx = content.find("(", if_idx)
            if open_paren_idx == -1:
                start_search = if_idx + 2
                continue
            
            between_text = content[if_idx+2:open_paren_idx]
            if between_text.strip() != "":
                start_search = open_paren_idx + 1
                continue
            
            close_paren_idx = content.find(")", open_paren_idx)
            if close_paren_idx == -1:
                start_search = open_paren_idx + 1
                continue
            
            start_condition = f"1.0+{open_paren_idx+1}c"
            end_condition = f"1.0+{close_paren_idx}c"
            self.text_widget.tag_add("condition", start_condition, end_condition)
            
            start_search = close_paren_idx + 1

    def convert_to_drawio(self):
        # Retrieve the content of the text widget (PlantUML code)
        plantuml_code = self.text_widget.get("1.0", tk.END)
        if not plantuml_code.strip():
            self.message_label.config(text="No PlantUML code available for conversion.")
            return

        try:
            # Parse PlantUML code into nodes and edges
            nodes, edges = parse_plantuml_activity(plantuml_code)
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
                self.message_label.config(text=f"Draw.io file created: {save_path}")
            else:
                self.message_label.config(text="Save cancelled.")
        except Exception as e:
            self.message_label.config(text=f"Error during conversion: {e}")

def main():
    root = tk.Tk()
    # Set application title in the menu bar
    root.tk.call('tk', 'appname', 'plantuml2drawio')
    
    import sys
    # Set icon in a cross-platform manner
    if sys.platform.startswith('win'):
        try:
            root.iconbitmap("p2dapp_icon.ico")
        except Exception as e:
            print("Error loading icon on Windows:", e)
    else:
        try:
            icon = tk.PhotoImage(file="p2dapp_icon.png")
            root.iconphoto(False, icon)
        except Exception as e:
            print("Error loading icon on macOS/Linux:", e)

    app = FileSelectorApp(root)
    
    # Bring window to the front and force focus
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 