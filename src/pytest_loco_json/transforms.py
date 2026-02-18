"""JSON content transformers.

This module provides a DSL extension that allows extracting data
from structured values using JSONPath expressions. The transformer
can return either all matched items or a single selected value
depending on configuration.
"""

from typing import TYPE_CHECKING, Literal

import jsonpath

from pytest_loco.extensions import Attribute, ContentTransformer, Schema

if TYPE_CHECKING:
    from collections.abc import Mapping

if TYPE_CHECKING:
    from jsonpath import JSON

if TYPE_CHECKING:
    from pytest_loco.values import RuntimeValue


def jsonpath_query(value: 'JSON', params: 'Mapping[str, RuntimeValue]') -> 'RuntimeValue':
    """Query a value using a JSONPath expression.

    The function applies a JSONPath query to the provided value and
    returns either all matched items or a single item based on
    transformer parameters.

    Args:
        value: Input value to query.
        params: Transformer parameters.

    Returns:
        Query results.
    """
    query = params.get('query')
    if not isinstance(query, str):
        return None

    items = jsonpath.findall(query, value)
    if not params.get('exact_one'):
        return items

    if not items:
        return None

    result = None
    match params.get('exact_mode'):
        case 'first':
            result = items[0]
        case 'last':
            result = items[-1]

    return result


query = ContentTransformer(
    transformer=jsonpath_query,
    name='query',
    field=Attribute(
        base=str,
        aliases=['find', 'select'],
        required=True,
        title='JSONPath expression',
        description=(
            'JSONPath expression used to extract values from the input '
            'data structure.'
        ),
    ),
    parameters=Schema({
        'exact_one': Attribute(
            base=bool,
            aliases=['exactOne', 'selectOne'],
            default=True,
            title='Return a single value',
            description=(
                'If enabled, the transformer returns a single matched '
                'value instead of a list. If multiple matches are found, '
                'the selection strategy is controlled by `exact_mode`. '
                'If no matches are found, `None` is returned.'
            ),
        ),
        'exact_mode': Attribute(
            base=Literal['first', 'last'],
            aliases=['exactMode', 'selectMode', 'mode'],
            default='first',
            examples=['first', 'last'],
            title='Single-value selection strategy',
            description=(
                'Defines how a single value is selected when multiple '
                'matches are found and ``exact_one`` is enabled. '
                'Possible values are ``first`` and ``last``.'
            ),
        ),
    }),
)
