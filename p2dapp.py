import tkinter as tk
from tkinter import filedialog
import os
import tempfile
from pumltodrawio import parse_plantuml, create_drawio_xml

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("plantuml to draw.io")
        self.root.geometry("600x400")  # Window size: 600x400

        # Configure grid: the right column (for file name and text widget) expands.
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Frame for the buttons on the left side
        self.left_frame = tk.Frame(root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # "Select File" button in the left frame, same width
        self.file_button = tk.Button(self.left_frame, text="Select File", command=self.open_file)
        self.file_button.pack(fill='x', pady=(0, 5))

        # "Convert to draw.io" button directly below the first button, also same width
        self.convert_button = tk.Button(self.left_frame, text="Convert to draw.io", command=self.convert_to_drawio)
        self.convert_button.pack(fill='x')

        # Frame for the right area (file name + text widget)
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        # Label above the text widget to display the file name
        self.filename_label = tk.Label(self.right_frame, text="No file selected.", anchor="w")
        self.filename_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Text component to display the file content
        self.text_widget = tk.Text(self.right_frame, wrap="word")
        self.text_widget.grid(row=1, column=0, sticky="nsew")

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
            except Exception as e:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, f"Error loading file:\n{e}")
        else:
            self.filename_label.config(text="No file selected.")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, "No file selected.")

    def convert_to_drawio(self):
        # Retrieve content of the text widget (PlantUML code)
        plantuml_code = self.text_widget.get("1.0", tk.END)
        if not plantuml_code.strip():
            self.text_widget.insert(tk.END, "\nNo PlantUML code available for conversion.\n")
            return

        # Write to a temporary file, since parse_plantuml() expects a filename
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".puml", encoding="utf-8") as tmp:
            tmp.write(plantuml_code)
            tmp_filename = tmp.name

        try:
            # Parse PlantUML code to convert it into nodes and edges
            nodes, edges = parse_plantuml(tmp_filename)
            # Generate XML for draw.io
            drawio_xml = create_drawio_xml(nodes, edges)

            # Show save dialog to select location for the draw.io file
            save_path = filedialog.asksaveasfilename(
                title="Save draw.io file",
                defaultextension=".xml",
                filetypes=[("XML Files", "*.xml")]
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
            # Delete temporary file when it's no longer needed
            os.remove(tmp_filename)

def main():
    root = tk.Tk()
    app = FileSelectorApp(root)
    
    # Bring window to front and force focus
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.focus_force())
    root.after(500, lambda: root.attributes("-topmost", False))
    
    root.mainloop()

if __name__ == "__main__":
    main() 