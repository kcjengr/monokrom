# Configuration file for the Sphinx documentation builder.
#
# For the full list of built configurations see the documentation (https://www.sphinx-doc.org/en/stable/config.html).

# -- Project information -----------------------------------------------------
project = "MonoKrom Plasma"
copyright = "2024, Kurt Jacobson, James Walker"
author = "Kurt Jacobson, James Walker"
release = "0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.graphviz",
]

myst_enable_extensions = [
    "colon_fence",
    "substitution",
    "linkify",
]

myst_fence_as_directive = [
    "graphviz",
]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_sidebars = {
    "**": ["globaltoc.html", "relations.html", "searchbox.html"]
}

# -- Options for myst_parser -------------------------------------------------
myst_heading_anchors = 3
