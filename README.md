# PlantUML to Draw.io Converter

This Python project allows the conversion of PlantUML activity diagrams into the Draw.io XML format. It offers both an easy-to-use graphical user interface (GUI) based on Tkinter and a command-line interface (CLI) for direct usage.

## Features

- **Diagram Conversion:** Converts simple PlantUML activity diagrams into Draw.io XML.
- **Graphical User Interface (GUI):** Select a PlantUML file, display its content, and convert it with just a few clicks.
- **Command-Line Interface (CLI):** Convert files directly via the terminal.
- **Conditional Processing:** Processes if-conditions, nested conditions, and activities.
- **Temporary File Management:** Uses temporary files for safe conversion and automatically cleans them up.

## Installation

1. **Prerequisites:**  
   - Python 3.6 or higher  
   - Tkinter (typically included with standard Python installations)

2. **Clone the Repository:**  
   Open your terminal and run:
   ```bash
   git clone https://github.com/your-username/your-repository.git
   ```

3. **Navigate to the Project Directory:**
   ```bash
   cd your-repository
   ```

## Usage

### Graphical User Interface (GUI)

1. Launch the GUI application:
   ```bash
   python p2dapp.py
   ```
2. Click on **"Select File"** to load a PlantUML file (supported file types include *.puml, *.plantuml, *.uml, *.txt).
3. The content of the file will be displayed in the text area.
4. Click **"Convert to draw.io"** to convert the PlantUML code into Draw.io XML format and choose a location to save the generated file.

### Command-Line Interface (CLI)

You can also convert files directly via the command line:

```bash
python pumltodrawio.py <input_plantuml_file> <output_drawio_file>
```
Example:
```bash
python pumltodrawio.py testdata/test3.puml output.xml
```

## Examples

The `testdata` folder contains example PlantUML files (such as `test1.puml`, `test2.puml`, and `test3.puml`) that you can use to test the functionality.

## Contributors

- Konrad Krafft
- ...

## License

This project is licensed under the MIT License. Please see the [LICENSE](LICENSE) file for details. 

# Creating platform specific executables

**Converting 'p2dapp' into a Native Executable Using PyInstaller**

1. **Installation**  
   Install PyInstaller using pip:
   ```bash
   pip install pyinstaller
   ```

2. **Creating the Executable**  
   Navigate to the directory containing the 'p2dapp.py' file and run for MacOS executable:
   ```bash
   pyinstaller --onefile --noconsole --icon=p2dapp_icon.icns p2dapp.py
   ```
   and for Windows and Linux executables:
   ```bash
   pyinstaller --onefile --noconsole --icon=p2dapp_icon.ico p2dapp.py
   ```
   
   - The `--onefile` flag bundles all dependencies into a single executable.
   - The `--noconsole` flag prevents the console window from appearing, which is ideal for GUI applications built with tkinter. (Omit this flag if you need the console for debugging.)

3. **Verifying the Build**  
   After the process completes, you will find the executable in the `dist` directory. Test the executable on your system to ensure it works as expected.

4. **Additional Notes**  
   - **Platform Specific**: The generated executable is platform-specific, meaning you need to build separate executables for Windows, macOS, and Linux.
   - **adding icon file to the executable**: add the icon file to the project directory and add the following option to the pyinstaller command: 
     - `--icon=p2dapp_icon.ico` in case of Windows or Linux
     - `--icon=p2dapp_icon.icns` in case of macOS
   - **Testing on a Clean System**: It's recommended to test the build on a system without Python installed to ensure that all dependencies are correctly bundled.

