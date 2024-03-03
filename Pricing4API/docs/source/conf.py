# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
##sys.path.append('C:\\Users\\Daniel\\OneDrive - UNIVERSIDAD DE SEVILLA\\Documentos\\Escritorio\\SandBox\\Repos\\Pricing4API')
sys.path.insert(0, os.path.abspath('C:\\Users\\Daniel\\OneDrive - UNIVERSIDAD DE SEVILLA\\Documentos\\Escritorio\\SandBox\\Repos\\Pricing4API'))
sys.path.insert(0, os.path.abspath('C:\\Users\\Daniel\\OneDrive - UNIVERSIDAD DE SEVILLA\\Documentos\\Escritorio\\SandBox\\Repos\\Pricing4API\\Pricing4API'))
print(sys.path)

project = 'Pricing4API'
copyright = '2024, dani'
author = 'dani'
release = '0.2.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx_markdown_builder',
    'recommonmark',
]

# Configuración para la extensión Napoleon, para habilitar el estilo Google
napoleon_google_docstring = True
napoleon_use_rtype = False
napoleon_use_ivar = True

# El sufijo de archivos de origen, puede ser una lista de sufijos si soportas múltiples formatos
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


