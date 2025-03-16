"""GUI application for converting PlantUML diagrams to Draw.io format."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from plantuml2drawio.config import (DIAGRAM_TYPE_ACTIVITY, DIAGRAM_TYPE_CLASS,
                                    DIAGRAM_TYPE_SEQUENCE,
                                    DIAGRAM_TYPE_UNKNOWN,
                                    FILE_EXTENSION_DRAWIO,
                                    FILE_EXTENSION_PLANTUML)
from plantuml2drawio.core import (determine_plantuml_diagram_type,
                                  process_diagram, read_plantuml_file)
from plantuml2drawio.processors.activity_processor import (
    create_activity_drawio_xml, layout_activity_diagram,
    parse_activity_diagram)

# Version number as constant
VERSION = "1.2.0"

# Import function from the new module with the new name
from plantuml2drawio.processors.activity_processor import (
    is_valid_activity_diagram, layout_activity_diagram, parse_activity_diagram)


class App(tk.Tk):
    """Main application window for the PlantUML to Draw.io converter."""

    def __init__(self):
        """Initialize the application window."""
        super().__init__()

        self.title("PlantUML to Draw.io Converter")
        self.geometry("800x600")

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create and configure all widgets in the application."""
        # Create top frame for buttons
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Create buttons
        self.create_buttons()

        # Create text area
        self.create_text_area()

        # Create status bar
        self.create_status_bar()

    def create_buttons(self):
        """Create and configure all buttons."""
        # Open file button
        self.open_button = ttk.Button(
            self.top_frame, text="Open PlantUML File", command=self.open_file
        )
        self.open_button.pack(side=tk.LEFT, padx=(0, 5))

        # Save file button
        self.save_button = ttk.Button(
            self.top_frame,
            text="Save as Draw.io",
            command=self.save_file,
            state=tk.DISABLED,
        )
        self.save_button.pack(side=tk.LEFT)

    def create_text_area(self):
        """Create and configure the text area."""
        # Create text widget with scrollbar
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.grid(row=1, column=0, sticky="nsew")
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)

        self.text_area = tk.Text(self.text_frame, wrap=tk.WORD, undo=True)
        self.text_area.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.VERTICAL, command=self.text_area.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_area["yscrollcommand"] = scrollbar.set

        # Bind text changes to update function
        self.text_area.bind("<<Modified>>", lambda e: self.on_text_modified())

    def create_status_bar(self):
        """Create and configure the status bar."""
        self.status_bar = ttk.Label(self.main_frame, text="Ready", anchor=tk.W)
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def on_text_modified(self):
        """Handle text modifications in the text area."""
        if self.text_area.edit_modified():
            self.update_text_and_button_state()
            self.text_area.edit_modified(False)

    def open_file(self):
        """Open and read a PlantUML file."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("PlantUML files", f"*{FILE_EXTENSION_PLANTUML}"),
                ("All files", "*.*"),
            ]
        )
        if file_path:
            try:
                content = read_plantuml_file(file_path)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.status_bar["text"] = f"Opened: {file_path}"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def save_file(self):
        """Save the current content as a Draw.io file."""
        content = self.text_area.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No content to save")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=FILE_EXTENSION_DRAWIO,
            filetypes=[
                ("Draw.io files", f"*{FILE_EXTENSION_DRAWIO}"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            try:
                process_diagram(content, file_path)
                self.status_bar["text"] = f"Saved: {file_path}"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def update_text_and_button_state(self):
        """Update the text area and button state based on the current content."""
        content = self.text_area.get("1.0", tk.END).strip()
        diagram_type = determine_plantuml_diagram_type(content)

        # Update status bar with diagram type
        type_text = {
            DIAGRAM_TYPE_ACTIVITY: "Activity Diagram",
            DIAGRAM_TYPE_SEQUENCE: "Sequence Diagram",
            DIAGRAM_TYPE_CLASS: "Class Diagram",
            DIAGRAM_TYPE_UNKNOWN: "Unknown Diagram Type",
        }.get(diagram_type, "Unknown Diagram Type")

        self.status_bar["text"] = f"Diagram Type: {type_text}"

        # Enable save button only for activity diagrams
        self.save_button["state"] = (
            tk.NORMAL if diagram_type == DIAGRAM_TYPE_ACTIVITY else tk.DISABLED
        )


def main():
    """Start the PlantUML to Draw.io converter application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
