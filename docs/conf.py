# This file is part of Progress API.
# Copyright (C) 2023 - 2024 Drexel University and contributors
# Licensed under the MIT license, see LICENSE.md for details.
# SPDX-License-Identifier: MIT

import os
import sys
sys.path.insert(0, os.path.abspath(".."))

import xshaper

project = "eXperiment Shaperate"
copyright = "2024 Drexel University"
author = "Michael D. Ekstrand"

release = xshaper.__version__

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph",
]

source_suffix = ".rst"

pygments_style = "sphinx"
highlight_language = "python3"

html_theme = "furo"
html_theme_options = {
}
templates_path = ["_templates"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "psutil": ("https://psutil.readthedocs.io/en/stable/", None),
}

autodoc_default_options = {
    "members": True,
    "member-order": "bysource"
}
autodoc_typehints = "description"
