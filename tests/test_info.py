#!/usr/bin/env python3

import os
import subprocess
import tempfile

from .diagram_examples import (activity_diagram, class_diagram,
                               component_diagram, erd_diagram, sequence_diagram,
                               state_diagram, usecase_diagram)

# Create a temporary directory for test files
with tempfile.TemporaryDirectory() as temp_dir:

    # Create test files for each diagram type
    test_files = {
        "activity.puml": activity_diagram,
        "sequence.puml": sequence_diagram,
        "class.puml": class_diagram,
        "usecase.puml": usecase_diagram,
        "component.puml": component_diagram,
        "state.puml": state_diagram,
        "erd.puml": erd_diagram,
        "invalid.txt": "This is not a PlantUML file.",
    }

    # Write test files
    for filename, content in test_files.items():
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)

    # Test each file with --info flag
    print("Testing --info flag with different diagram types:")
    print("-" * 50)

    for filename in test_files.keys():
        file_path = os.path.join(temp_dir, filename)
        print(f"\nFile: {filename}")

        cmd = ["python3", "p2dcore.py", "--input", file_path, "--info"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Display output
        print("Output:")
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")

        # Display exit code
        print(f"Exit code: {result.returncode}")

    # Test conversion of activity diagram
    print("\nTesting conversion of activity diagram:")
    print("-" * 50)

    activity_file = os.path.join(temp_dir, "activity.puml")
    output_file = os.path.join(temp_dir, "activity.drawio")

    cmd = ["python3", "p2dcore.py", "--input", activity_file, "--output", output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("Output:")
    for line in result.stdout.strip().split("\n"):
        print(f"  {line}")

    print(f"Exit code: {result.returncode}")
    print(f"Output file exists: {os.path.exists(output_file)}")

    # Test attempted conversion of sequence diagram (should fail)
    print("\nTesting attempted conversion of sequence diagram (should fail):")
    print("-" * 50)

    sequence_file = os.path.join(temp_dir, "sequence.puml")
    output_file = os.path.join(temp_dir, "sequence.drawio")

    cmd = ["python3", "p2dcore.py", "--input", sequence_file, "--output", output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("Output:")
    for line in result.stdout.strip().split("\n"):
        print(f"  {line}")

    print(f"Exit code: {result.returncode}")
    print(f"Output file exists: {os.path.exists(output_file)}")

print("\nTesting completed.")
