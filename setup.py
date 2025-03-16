"""Setup script for the plantuml2drawio package."""

from setuptools import find_packages, setup

setup(
    name="plantuml2drawio",
    version="0.1.0",
    description="A tool for converting PlantUML diagrams to Draw.io format",
    author="doubleSlash Net-Business GmbH",
    author_email="info@doubleSlash.de",
    url="https://github.com/doubleSlash-net/plantuml2drawio",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "customtkinter>=5.2.3",
        "pillow>=10.3.0",
        # pyinstaller is only needed for creating the executable and should not
        # be installed as a direct dependency
    ],
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "p2d-cli=plantuml2drawio.core:main",
            "p2d-gui=plantuml2drawio.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
