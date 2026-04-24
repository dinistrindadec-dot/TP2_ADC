# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "Biblioteca TP2"
copyright = "2026, TP2 ADC"
author = "TP2 ADC"
version = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "pt"

html_theme = "nature"
html_static_path = ["_static"]

todo_include_todos = True
