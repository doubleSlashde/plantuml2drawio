import tkinter as tk
from tkinter import filedialog
import os
import tempfile
from p2dcore import parse_plantuml, create_drawio_xml
import tkinter.font as tkFont

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PlantUML to Draw.io Converter")
        self.root.geometry("800x600")  # Larger window for better overview

        # Create menu bar for additional convenience
        self.create_menubar()

        # Configure main grid
        self.root.columnconfigure(0, weight=1)
        # Set row 2 (the main frame) to be expandable
        self.root.rowconfigure(2, weight=1)

        # Row 0: File name label
        self.filename_label = tk.Label(
            self.root, 
            text="No file selected.",
            anchor="w",
            font=("Arial", 12)
        )
        self.filename_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Row 1: Message label (for notifications and errors)
        self.message_label = tk.Label(
            self.root, 
            text="",
            anchor="w",
            font=("Arial", 12)
        )
        self.message_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Row 2: Main frame for text widget and scrollbar to ensure responsive design
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Set default font for the text widget
        self.default_font = tkFont.Font(family="Courier New", size=14)
        
        # Text widget to display file content
        self.text_widget = tk.Text(
            self.main_frame, 
            wrap="word",
            font=self.default_font
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        self.text_widget.tag_configure("plantuml", foreground="#800000", font=self.default_font)
        self.text_widget.tag_configure("keyword", foreground="#F000F0", font=self.default_font)
        self.text_widget.bind("<KeyRelease>", lambda event: self.highlight_plantuml())

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

        # "Convert to Draw.io" button on the right
        self.convert_button = tk.Button(self.button_frame, text="Convert to Draw.io", command=self.convert_to_drawio)
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

        # Variable to store current file name (without extension)
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
        # Method to open files
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("PlantUML and Text Files", ("*.puml", "*.txt", "*.plantuml", "*.uml"))]
        )
    
        if file_path:
            # Store the current file name without extension
            self.current_file = os.path.splitext(os.path.basename(file_path))[0]
            self.filename_label.config(text=f"Loaded file: {os.path.basename(file_path)}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                # Clear any previous message
                self.message_label.config(text="File loaded successfully.")
            except Exception as e:
                content = ""
                self.message_label.config(text=f"Error loading file: {e}")
        else:
            self.filename_label.config(text="No file selected.")
            content = ""
            self.message_label.config(text="No file selected.")
    
        # Display file content in the text widget
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, content)
        # Always perform highlighting regardless of the content
        self.highlight_plantuml()

    def highlight_plantuml(self):
        """Highlights specific keywords in the text widget using clear magenta (#F000F0)."""
        # Remove existing highlights with the "keyword" tag
        self.text_widget.tag_remove("keyword", "1.0", tk.END)
        
        # List of keywords to be highlighted
        for pattern in ["if", "then", "else", "endif", "start", "stop", "@startuml", "@enduml"]:
            start_idx = "1.0"
            while True:
                pos = self.text_widget.search(pattern, start_idx, stopindex=tk.END)
                if not pos:
                    break
                end_pos = f"{pos}+{len(pattern)}c"
                self.text_widget.tag_add("keyword", pos, end_pos)
                start_idx = end_pos

    def convert_to_drawio(self):
        # Retrieve the content of the text widget (PlantUML code)
        plantuml_code = self.text_widget.get("1.0", tk.END)
        if not plantuml_code.strip():
            self.message_label.config(text="No PlantUML code available for conversion.")
            return

        try:
            # Parse PlantUML code directly as a string
            nodes, edges = parse_plantuml(plantuml_code)
            # Generate XML for draw.io
            drawio_xml = create_drawio_xml(nodes, edges)

            # Determine default file name
            default_filename = f"{self.current_file}.drawio" if self.current_file else "untitled.drawio"

            # Show save dialog to select location for the draw.io file
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
    import sys
    # Set the icon cross-platform:
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
    
    # Bring window to front and force focus
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 