import os
import sys
from unittest.mock import MagicMock
import sphinx_rtd_theme

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath('..'))  # Adjust the path if necessary

sys.modules['config'] = MagicMock()

project = 'Reputation Game v2'
copyright = '2024 - Torsten Enßlin, Viktoria Kainz, Florian Wiethof'
author = 'Torsten Enßlin, Viktoria Kainz, Florian Wiethof'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_css_files = [
    'custom.css',  # Your custom CSS file
]

html_theme_options = {
    'navigation_with_keys': True,  # Enable keyboard navigation (optional)
    'collapse_navigation': True,   # Keep the navigation bar expanded (optional)
    'sticky_navigation': True,      # Enable sticky navigation (optional)
    'includehidden': True,          # Include hidden documents in the TOC (optional)
    'titles_only': False,           # Display full titles in TOC (optional)
}