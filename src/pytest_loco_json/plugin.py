"""JSON plugin for pytest-loco DSL.

This module defines the `json` plugin that provides JSON content
support and JSONPath-based instructions for querying data structures.
"""

from pytest_loco.extensions import Plugin

from .format import json_format
from .instructions import jsonpath_query

json = Plugin(
    name='json',
    content_types=[json_format],
    instructions=[jsonpath_query],
)
