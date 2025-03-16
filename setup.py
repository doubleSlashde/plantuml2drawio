"""Setup script for the plantuml2drawio package."""

from setuptools import find_packages, setup

setup(
    name="plantuml2drawio",
    version="1.2.0",
    description="A tool for converting PlantUML diagrams to Draw.io format",
    author="doubleSlash.de",
    author_email="info@doubleSlash.de",
    url="https://github.com/doubleSlash-net/plantuml2drawio",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "customtkinter>=5.2.2",
        "pillow>=10.3.0",
        # pyinstaller is only needed for creating the executable and should not
        # be installed as a direct dependency
    ],
    include_package_data=True,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "p2d-cli=plantuml2drawio.core:main",
            "p2d-gui=plantuml2drawio.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
