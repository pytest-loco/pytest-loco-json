"""JSONPath instruction for the DSL.

This module defines a DSL instruction `jq` that allows compiling
JSONPath expressions from YAML scalar nodes. The resulting instruction
can be used to query values from complex data structures at runtime.
It ensures that parsing and compilation errors are wrapped in
`DSLSchemaError` with proper YAML context.
"""

from typing import TYPE_CHECKING

import jsonpath
import yaml

from pytest_loco.errors import DSLSchemaError
from pytest_loco.extensions import Instruction

if TYPE_CHECKING:
    from collections.abc import Mapping

if TYPE_CHECKING:
    from pytest_loco.schema import YAMLLoader, YAMLNode
    from pytest_loco.values import Deferred, RuntimeValue


def jsonpath_query_constructor(loader: 'YAMLLoader', node: 'YAMLNode') -> 'Deferred[RuntimeValue]':
    """Construct a precompiled JSONPath expression from a YAML scalar node.

    This function is intended to be used as a YAML instruction constructor
    in the DSL. It reads a scalar string from the YAML node, compiles it
    into a JSONPath expression, and returns a deferred callable that can
    be executed at runtime to query a value.

    Args:
        loader: YAML loader instance used to parse the document.
        node: YAML scalar node containing the JSONPath expression.

    Returns:
        A deferred JSONPath object that can be called with a target value
        to evaluate the expression.

    Raises:
        DSLSchemaError: If the JSONPath expression is invalid or
            the YAML node cannot be processed.
    """
    try:
        variable, query_string = loader.construct_scalar(node).split(' ', 1)
        query = jsonpath.compile(query_string)

    except yaml.MarkedYAMLError as base:
        raise DSLSchemaError.from_yaml_error(base) from base

    except Exception as base:
        raise DSLSchemaError.from_yaml_node('Invalid variable or JSONPath', node) from base

    def resolver(context: 'Mapping[str, RuntimeValue]') -> 'RuntimeValue':
        """Wrapper for resolve a values by the JSONPath selector."""
        value = context.get(variable)
        if not value:
            return []

        return query.findall(value, filter_context=context)

    return resolver


jsonpath_query = Instruction(
    constructor=jsonpath_query_constructor,
    name='jsonpath',
)
