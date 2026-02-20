# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

# Change to project root so 'ntsm' can be imported as a package.
# This avoids conflicts with system modules like 'lib'.
sys.path.insert(0, os.path.abspath('../../src/ntsm'))


# -- Project information -----------------------------------------------------

project = 'ntsm'
copyright = '2024, Adrian Coman'
author = 'Adrian Coman'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc", # Core Sphinx library for auto html doc generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables for modules/classes/methods etc
    'sphinx.ext.intersphinx',  # Link to other project's documentation (see mapping below)
    "sphinx.ext.napoleon",
    # "sphinx.ext.viewcode", # Add a link to the Python source code for classes, functions etc.
    'sphinx_autodoc_typehints', # Automatically document param types (less noise in class signature)
    'nbsphinx',  # Integrate Jupyter Notebooks and Sphinx
    'IPython.sphinxext.ipython_console_highlighting',
    'sphinx_rtd_theme',
    'sphinx_github_alerts'
]

# Mappings for sphinx.ext.intersphinx. Projects have to have Sphinx-generated doc! (.inv file)
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
autosummary_generate = True  # Turn on sphinx.ext.autosummary
autosummary_generate_overwrite = True # overwrite
# autosummary_imported_members = True # import all modules used
autoclass_content = "class"  # Add __init__ doc (ie. params) to class summaries, "init", "both"
# autodoc_docstring_signature = True
html_copy_source = False
html_show_sourcelink = False  # Remove 'view source code' from top of page (for html, not python)
# autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
# set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
# nbsphinx_allow_errors = True  # Continue through Jupyter errors
# autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints
add_module_names = False # Remove namespaces from class/method signatures
add_function_parentheses = False   # optional but usually wanted
autoclass_content = "both"          

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': True,
    'exclude-members': '__init__,__weakref__,__dict__,__module__',
}
autosummary_generate = True  
suppress_warnings = ['autosummary.*']  
toc_object_entries_show_parents = 'hide'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

# Readthedocs theme
# on_rtd is whether on readthedocs.org, this line of code grabbed from docs.readthedocs.org...
# on_rtd = os.environ.get("READTHEDOCS", None) == "True"
# if not on_rtd:  # only import and set the theme if we're building docs locally
#     import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
# Success: This variable is required for rst2pdf but avoid get_html_theme_path() deprecation
# html_theme_path = [os.path.abspath(os.path.dirname(sphinx_rtd_theme.__file__))]
html_theme_options = {
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': True,
    'titles_only': False,
    'version_selector': False,
    'language_selector': False,
}
# html_logo = '_static/NTO_D_213_C.png'
html_css_files = ["custom-readthedocs.css"] # Override some CSS settings
numfig = True
smart_quotes = True
html_use_smartypants = True

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']




